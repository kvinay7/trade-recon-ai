from matcher.deterministic import deterministic
from matcher.fuzzy import fuzzy_score
from matcher.explain import explain
from models import row_to_trade
import pandas as pd

def reconcile_multi_source(central_df, other_sources: dict):
    """
    central_df = dataframe chosen as central
    other_sources = dict { source_name: dataframe }
    """
    results = {}

    trades_central = [row_to_trade(r, "central") for _, r in central_df.iterrows()]

    for src_name, df in other_sources.items():

        trades_src = [row_to_trade(r, src_name) for _, r in df.iterrows()]

        summary = []
        for a in trades_src:
            best_score = -1
            best_b = None
            best_type = "unmatched"

            # try exact match
            for b in trades_central:
                if deterministic(a, b):
                    summary.append({
                        "type": "exact",
                        "score": 1.0,
                        "src": a.to_dict(),
                        "central": b.to_dict(),
                        "explanation": "Exact ID match"
                    })
                    break
            else:
                # fuzzy search
                for b in trades_central:
                    score = fuzzy_score(a, b)
                    if score > best_score:
                        best_score = score
                        best_b = b
                
                if best_score >= 0.85:
                    summary.append({
                        "type": "auto_match",
                        "score": best_score,
                        "src": a.to_dict(),
                        "central": best_b.to_dict(),
                        "explanation": explain(a.to_dict(), best_b.to_dict(), best_score)
                    })
                elif 0.5 <= best_score < 0.85:
                    summary.append({
                        "type": "review",
                        "score": best_score,
                        "src": a.to_dict(),
                        "central": best_b.to_dict(),
                        "explanation": explain(a.to_dict(), best_b.to_dict(), best_score)
                    })
                else:
                    summary.append({
                        "type": "unmatched",
                        "score": best_score,
                        "src": a.to_dict(),
                        "central": None,
                        "explanation": explain(a.to_dict(), {}, best_score)
                    })

        results[src_name] = pd.DataFrame(summary)

    return results
