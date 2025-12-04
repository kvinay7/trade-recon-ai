from rapidfuzz import fuzz

def fuzzy_score(a, b):
    cp = fuzz.token_set_ratio(a.counterparty, b.counterparty) / 100
    amt = 1 - abs(a.amount - b.amount) / max(a.amount, b.amount, 1)
    date = 1 if abs((a.trade_date - b.trade_date).days) <= 1 else 0

    return round((0.5 * amt) + (0.3 * cp) + (0.2 * date), 3)
