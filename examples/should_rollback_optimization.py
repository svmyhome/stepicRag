def should_rollback_optimization(metrics: dict) -> bool:
    if any([metrics["faithfulness"] < 0.85, metrics["latency_ms"] > 500, metrics["not_found_rate"] > 0.3]):
        return True
    return False
