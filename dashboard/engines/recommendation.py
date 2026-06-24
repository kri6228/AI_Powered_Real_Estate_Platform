# dashboard/engines/recommendation.py

def calculate_roi(actual_price, predicted_price):
    """
    ROI = (predicted - actual) / actual * 100
    Positive ROI = undervalued (good buy)
    Negative ROI = overvalued (consider sell)
    """
    roi = ((predicted_price - actual_price) / actual_price) * 100
    return round(float(roi), 2)


def get_recommendation(roi, risk_score, availability_status):
    """
    BUY  — High ROI + Low Risk + Undervalued
    HOLD — Medium ROI or Medium Risk
    SELL — Low/Negative ROI + High Risk

    Returns recommendation, reason list, and color
    """

    reasons = []

    # ── BUY CONDITIONS ────────────────────────────────────
    if roi >= 15 and risk_score <= 3.3:
        recommendation = 'BUY'
        color = 'green'
        emoji = '✅'
        reasons.append(f"High ROI of {roi:.1f}% — property is undervalued")
        reasons.append(f"Low risk score ({risk_score}/10) — safe investment")
        if availability_status == 'Ready_to_Move':
            reasons.append("Ready to move — immediate possession possible")

    # ── SELL CONDITIONS ───────────────────────────────────
    elif roi < 0 and risk_score > 6.6:
        recommendation = 'SELL'
        color = 'red'
        emoji = '🔴'
        reasons.append(f"Negative ROI of {roi:.1f}% — property is overvalued")
        reasons.append(f"High risk score ({risk_score}/10) — risky investment")
        if availability_status == 'Under_Construction':
            reasons.append("Under construction — adds delivery and market risk")

    elif roi < 0 and risk_score > 5:
        recommendation = 'SELL'
        color = 'red'
        emoji = '🔴'
        reasons.append(f"Negative ROI of {roi:.1f}% — not worth current price")
        reasons.append(f"Above average risk ({risk_score}/10)")

    # ── HOLD CONDITIONS ───────────────────────────────────
    elif roi >= 5 and risk_score <= 6.6:
        recommendation = 'HOLD'
        color = 'orange'
        emoji = '🟡'
        reasons.append(f"Moderate ROI of {roi:.1f}% — some upside potential")
        reasons.append(f"Medium risk ({risk_score}/10) — monitor market trends")
        if availability_status == 'Under_Construction':
            reasons.append("Under construction — wait for possession before selling")

    elif roi >= 15 and risk_score > 3.3:
        recommendation = 'HOLD'
        color = 'orange'
        emoji = '🟡'
        reasons.append(f"Good ROI of {roi:.1f}% but risk is elevated ({risk_score}/10)")
        reasons.append("Consider buying only after risk factors improve")

    else:
        recommendation = 'HOLD'
        color = 'orange'
        emoji = '🟡'
        reasons.append(f"ROI of {roi:.1f}% — marginal returns")
        reasons.append(f"Risk score {risk_score}/10 — neutral outlook")
        reasons.append("Wait for better market conditions")

    return {
        'recommendation': recommendation,
        'color': color,
        'emoji': emoji,
        'roi': roi,
        'reasons': reasons
    }