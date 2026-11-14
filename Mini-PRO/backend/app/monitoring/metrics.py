from prometheus_client import Counter, Gauge, Histogram

# Prometheus Metrics
WORKFLOWS_TOTAL = Counter(
    "safety_engine_workflows_total",
    "Total number of workflows created",
    ["agent_type", "status"],
)

STEPS_TOTAL = Counter(
    "safety_engine_steps_total",
    "Total number of steps evaluated",
    ["tool_name", "decision"],
)

SAFETY_EVENTS_TOTAL = Counter(
    "safety_engine_safety_events_total",
    "Total safety events triggered",
    ["event_type", "severity"],
)

APPROVALS_TOTAL = Counter(
    "safety_engine_approvals_total",
    "Total approval actions processed",
    ["action"],  # approved, rejected
)

WORKFLOW_DURATION_HISTOGRAM = Histogram(
    "safety_engine_workflow_duration_seconds",
    "Duration of workflows in seconds",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
)

ACTIVE_WORKFLOWS_GAUGE = Gauge(
    "safety_engine_active_workflows",
    "Current number of actively executing workflows",
)
