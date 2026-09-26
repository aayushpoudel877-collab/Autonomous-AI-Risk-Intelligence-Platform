from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path

@dataclass(frozen=True)
class ModelRecord:
    name: str
    version: str
    stage: str
    metric: float
    created_at: str

class ModelRegistry:
    def __init__(self, path: str="data/model_registry.json"):
        self.path=Path(path)

    def register(self,name:str,version:str,stage:str,metric:float):
        records=self._load()
        record=ModelRecord(name,version,stage,float(metric),datetime.now(timezone.utc).isoformat())
        records.append(asdict(record))
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(records,indent=2))
        return record

    def list(self):
        return self._load()

    def _load(self):
        if not self.path.exists(): return []
        return json.loads(self.path.read_text())
