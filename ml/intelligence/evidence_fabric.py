import json
import os
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

from ml.intelligence.knowledge_graph import Edge, KnowledgeGraph, Node
from ml.intelligence.provenance import EvidenceLink
from ml.intelligence.temporal import build_timeline


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    modality: str
    source: str
    content: str
    metadata: dict
    timestamp: str | None = None
    document_id: str | None = None
    vector_ref: str | None = None


class EvidenceFabric:
    """Durable evidence context shared by retrieval, graph, provenance and temporal services."""

    def __init__(self, path: str | None = None):
        self.path = path or os.getenv("AEGISMIND_EVIDENCE_DB", "data/evidence_fabric.db")
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS evidence_records (
                    evidence_id TEXT PRIMARY KEY,
                    modality TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    timestamp TEXT,
                    document_id TEXT,
                    vector_ref TEXT
                );
                CREATE TABLE IF NOT EXISTS fabric_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    label TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS fabric_edges (
                    source TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    target TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    PRIMARY KEY (source, relation, target)
                );
                CREATE TABLE IF NOT EXISTS evidence_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_evidence_document ON evidence_records(document_id);
                CREATE INDEX IF NOT EXISTS idx_edges_source ON fabric_edges(source);
                CREATE INDEX IF NOT EXISTS idx_edges_target ON fabric_edges(target);
                """
            )

    def _connect(self):
        return sqlite3.connect(self.path)

    def add_evidence(self, record: EvidenceRecord):
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO evidence_records
                (evidence_id, modality, source, content, metadata, timestamp, document_id, vector_ref)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (record.evidence_id, record.modality, record.source, record.content,
                 json.dumps(record.metadata, sort_keys=True), record.timestamp,
                 record.document_id, record.vector_ref),
            )
            connection.execute(
                "INSERT OR REPLACE INTO fabric_nodes (node_id, node_type, label) VALUES (?, ?, ?)",
                (record.evidence_id, "evidence", record.evidence_id),
            )
        return record

    def get_evidence(self, evidence_id: str):
        with self._connect() as connection:
            row = connection.execute(
                """SELECT evidence_id, modality, source, content, metadata, timestamp, document_id, vector_ref
                   FROM evidence_records WHERE evidence_id = ?""",
                (evidence_id,),
            ).fetchone()
        if not row:
            return None
        return EvidenceRecord(row[0], row[1], row[2], row[3], json.loads(row[4]), row[5], row[6], row[7])

    def add_node(self, node: Node):
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO fabric_nodes (node_id, node_type, label) VALUES (?, ?, ?)",
                (node.node_id, node.node_type, node.label),
            )
        return node

    def add_edge(self, edge: Edge):
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT node_id FROM fabric_nodes WHERE node_id IN (?, ?)",
                (edge.source, edge.target),
            ).fetchall()
            if len(exists) != 2:
                raise KeyError("both edge endpoints must exist in the evidence fabric")
            connection.execute(
                """INSERT OR REPLACE INTO fabric_edges
                   (source, relation, target, confidence) VALUES (?, ?, ?, ?)""",
                (edge.source, edge.relation, edge.target, float(edge.confidence)),
            )
        return edge

    def add_event(self, event: dict):
        event_id, timestamp = str(event["id"]), str(event["timestamp"])
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO evidence_events (event_id, timestamp, payload) VALUES (?, ?, ?)",
                (event_id, timestamp, json.dumps(event, sort_keys=True)),
            )
        return event

    def events(self):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM evidence_events ORDER BY timestamp ASC"
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def graph(self):
        graph = KnowledgeGraph()
        with self._connect() as connection:
            nodes = connection.execute("SELECT node_id, node_type, label FROM fabric_nodes").fetchall()
            edges = connection.execute("SELECT source, relation, target, confidence FROM fabric_edges").fetchall()
        for row in nodes:
            graph.add_node(Node(*row))
        for row in edges:
            graph.add_edge(Edge(*row))
        return graph

    def add_provenance(self, evidence_id: str, node_id: str, relation: str = "supports", confidence: float = 1.0):
        if self.get_evidence(evidence_id) is None:
            raise KeyError(evidence_id)
        if self.graph().nodes.get(node_id) is None:
            self.add_node(Node(node_id, "context", node_id))
        return self.add_edge(Edge(evidence_id, relation, node_id, max(0.0, min(1.0, float(confidence)))))

    def provenance_links(self):
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT source, relation, target, confidence FROM fabric_edges
                   WHERE source IN (SELECT evidence_id FROM evidence_records)"""
            ).fetchall()
        return [EvidenceLink(row[0], row[2], row[1], float(row[3]), "persisted") for row in rows]

    def context(self):
        events = self.events()
        return {
            "graph": self.graph(),
            "events": build_timeline(events) if events else [],
            "provenance_links": [asdict(link) for link in self.provenance_links()],
        }

    def stats(self):
        with self._connect() as connection:
            evidence = connection.execute("SELECT COUNT(*) FROM evidence_records").fetchone()[0]
            nodes = connection.execute("SELECT COUNT(*) FROM fabric_nodes").fetchone()[0]
            edges = connection.execute("SELECT COUNT(*) FROM fabric_edges").fetchone()[0]
            events = connection.execute("SELECT COUNT(*) FROM evidence_events").fetchone()[0]
        return {"evidence": int(evidence), "nodes": int(nodes), "edges": int(edges), "events": int(events)}
