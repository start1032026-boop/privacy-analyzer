def combine_results(results):

    scores = []
    red_flags = []

    for r in results:
        try:
            scores.append(int(r["risk_score"]))
            red_flags.extend(r["red_flags"])
        except Exception as e:
            print("Parsing error:", e)

    if scores:
        avg_score = sum(scores) / len(scores)
    else:
        avg_score = 0

    return {
        "final_risk_score": round(avg_score, 1),
        "top_red_flags": red_flags[:3]
    }