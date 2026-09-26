from ml.monitoring import InferenceMonitor

monitor=InferenceMonitor()

def record(score:float,started_at:float):
    monitor.observe(score,started_at)

def snapshot(): return monitor.snapshot()
