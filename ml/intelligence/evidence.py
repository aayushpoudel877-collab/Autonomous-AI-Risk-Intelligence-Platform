from dataclasses import dataclass,field

@dataclass
class EvidenceGraph:
    claims:dict=field(default_factory=dict)
    support:dict=field(default_factory=dict)

    def add_claim(self,claim_id,text):
        self.claims[claim_id]=text
        self.support.setdefault(claim_id,[])
    def attach(self,claim_id,evidence_ids):
        if claim_id not in self.claims: raise KeyError(claim_id)
        self.support[claim_id].extend(evidence_ids)
    def explain(self,claim_id):
        return {"claim_id":claim_id,"claim":self.claims[claim_id],"evidence":self.support.get(claim_id,[])}
