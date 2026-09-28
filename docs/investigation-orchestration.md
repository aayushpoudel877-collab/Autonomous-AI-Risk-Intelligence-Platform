# Investigation Orchestration

AegisMind now supports a bounded goal-driven investigation loop: goal, planned retrieval steps, evidence accumulation, deduplication, stopping condition, and trace output.

The planner uses deterministic perspectives for the original goal, causal context, and impact context. The orchestration contract is replaceable by a future agentic planner while keeping bounded execution and evidence provenance.

This layer does not treat retrieved evidence as verified truth or causal proof.