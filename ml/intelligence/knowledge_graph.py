from dataclasses import dataclass

@dataclass(frozen=True)
class Node:
    node_id:str
    node_type:str
    label:str

@dataclass(frozen=True)
class Edge:
    source:str
    relation:str
    target:str
    confidence:float=1.0

class KnowledgeGraph:
    def __init__(self):
        self.nodes={}
        self.edges=[]
    def add_node(self,node):
        self.nodes[node.node_id]=node
    def add_edge(self,edge):
        if edge.source in self.nodes and edge.target in self.nodes:
            self.edges.append(edge)
    def neighbors(self,node_id,relation=None):
        return [e for e in self.edges if e.source==node_id and (relation is None or e.relation==relation)]
    def subgraph(self,node_id,depth=1):
        seen={node_id}; frontier={node_id}
        for _ in range(depth):
            nxt=set()
            for e in self.edges:
                if e.source in frontier: nxt.add(e.target)
                if e.target in frontier: nxt.add(e.source)
            nxt-=seen; seen|=nxt; frontier=nxt
        return {"nodes":[self.nodes[n].__dict__ for n in seen if n in self.nodes],
                "edges":[e.__dict__ for e in self.edges if e.source in seen and e.target in seen]}
