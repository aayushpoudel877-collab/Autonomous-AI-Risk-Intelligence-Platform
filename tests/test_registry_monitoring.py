from ml.monitoring import InferenceMonitor
from ml.registry import ModelRegistry

def test_registry_roundtrip(tmp_path):
    registry=ModelRegistry(str(tmp_path/"models.json"))
    record=registry.register("risk-mlp","0.1","candidate",.82)
    assert record.version == "0.1"
    assert registry.list()[0]["name"] == "risk-mlp"

def test_monitor_snapshot():
    monitor=InferenceMonitor()
    import time
    start=time.perf_counter(); monitor.observe(.8,start)
    monitor.record_error()
    snapshot=monitor.snapshot()
    assert snapshot["requests"] == 1 and snapshot["errors"] == 1
