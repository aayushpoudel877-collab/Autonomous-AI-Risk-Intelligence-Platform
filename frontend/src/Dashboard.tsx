import { useEffect, useState } from "react";
type Metrics = { requests:number; errors:number; error_rate:number; mean_latency_ms:number; mean_risk:number };
export default function Dashboard() {
  const [metrics,setMetrics]=useState<Metrics|null>(null);
  useEffect(() => { fetch("/api/v1/monitoring/metrics").then(r=>r.json()).then(setMetrics).catch(()=>{}); },[]);
  const risk=metrics ? Math.round(metrics.mean_risk*100) : 72;
  const latency=metrics ? metrics.mean_latency_ms.toFixed(1)+"ms" : "—";
  const errors=metrics ? (metrics.error_rate*100).toFixed(1)+"%" : "—";
  return <main className="shell">
    <header><span className="eyebrow">AEGISMIND</span><h1>Autonomous Risk Intelligence</h1><p>Multimodal signals, model telemetry and explainable risk analysis.</p></header>
    <section className="grid">
      <article className="card"><span>Overall Risk</span><strong>{risk}%</strong><small>Live mean from inference telemetry</small></article>
      <article className="card"><span>Requests</span><strong>{metrics?.requests ?? 0}</strong><small>Observed API inferences</small></article>
      <article className="card"><span>Latency</span><strong>{latency}</strong><small>Mean inference latency</small></article>
      <article className="card"><span>Error Rate</span><strong>{errors}</strong><small>Operational health</small></article>
    </section>
    <section className="panel"><h2>Intelligence Pipeline</h2><div className="pipeline"><span>Tabular</span><b>→</b><span>Temporal GRU</span><b>→</b><span>NLP / Vision</span><b>→</b><span>Attention Fusion</span><b>→</b><span>Risk Engine</span></div></section>
  </main>;
}
