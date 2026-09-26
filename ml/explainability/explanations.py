from dataclasses import dataclass
@dataclass(frozen=True)
class Explanation:
    summary:str
    contributors:list[dict]
    caveats:list[str]

def explain_risk(signals:dict[str,float],score:float)->Explanation:
    ranked=sorted(signals.items(),key=lambda item:item[1],reverse=True)
    contributors=[{"signal":k,"value":round(float(v),4),"relative_weight":round(float(v)/sum(signals.values()),4) if sum(signals.values()) else 0} for k,v in ranked]
    level="high" if score>=.70 else "medium" if score>=.35 else "low"
    return Explanation(f"The fused model produced a {level}-risk assessment from the supplied signals.",contributors,["Signal contribution is not causal evidence.","Predictions should be reviewed with source context."])
