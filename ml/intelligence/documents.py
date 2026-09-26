from dataclasses import dataclass
from hashlib import sha256
import re

@dataclass(frozen=True)
class DocumentChunk:
    document_id:str
    chunk_id:str
    text:str
    source:str
    metadata:dict

def chunk_document(text,source="unknown",document_id=None,max_chars=800):
    document_id=document_id or sha256(text.encode()).hexdigest()[:16]
    parts=[p.strip() for p in re.split(r"\n\s*\n|(?<=[.!?])\s+",text) if p.strip()]
    chunks=[]; buf=""
    for part in parts:
        if len(buf)+len(part)+1<=max_chars: buf=(buf+" "+part).strip()
        else:
            if buf: chunks.append(buf)
            buf=part
    if buf: chunks.append(buf)
    return [DocumentChunk(document_id,f"{document_id}-{i}",p,source,{"chunk_index":i}) for i,p in enumerate(chunks)]

def ingest_text(text,source="unknown"):
    if not text or not text.strip(): raise ValueError("document text must not be empty")
    return chunk_document(text,source)
