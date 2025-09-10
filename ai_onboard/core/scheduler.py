def order_rules(rules, hist, profiler):
    # Higher expected fault yield first (fallback to default), prefer lower time
    def score(r):
        yf = hist.get(r["id"], {}).get("fault_yield", 0.05)
        t = profiler.get(r["id"], {}).get("p50_time", 0.2)
        return (yf + 1e-3) / (t + 1e-3)

    return sorted(rules, key=score, reverse=True)


def should_skip(rule, hist, impacted):
    # Skip if rule has 5 consecutive passes and is not impacted by changes
    stable = hist.get(rule["id"], {}).get("passes_in_row", 0) >= 5
    return stable and not impacted
