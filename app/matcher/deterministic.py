def deterministic(a, b):
    return a.trade_id == b.trade_id and a.trade_id != ""
