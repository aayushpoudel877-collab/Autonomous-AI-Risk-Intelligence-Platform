from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Entity:
    text:str
    entity_type:str
    start:int
    end:int

@dataclass(frozen=True)
class Relation:
    subject:str
    relation:str
    object:str

def extract_entities(text):
    entities=[]
    for m in re.finditer(r"\b[A-Z][A-Za-z0-9_-]{2,}\b",text):
        entities.append(Entity(m.group(),"proper_noun",m.start(),m.end()))
    for m in re.finditer(r"\b(?:server|database|router|service|model|api)\b",text,re.I):
        entities.append(Entity(m.group(),"system_component",m.start(),m.end()))
    return entities

def extract_relations(text):
    entities=extract_entities(text)
    return [Relation(a.text,"mentioned_with",b.text) for a,b in zip(entities,entities[1:])]
