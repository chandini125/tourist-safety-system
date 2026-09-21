def calculate_risk(
    zone_risk,
    speed,
    stationary_time,
    route_deviation,
    night_movement
):
    score = 0

    # Zone risk
    if zone_risk == "MEDIUM":
        score += 20
    elif zone_risk == "HIGH":
        score += 30
    elif zone_risk == "CRITICAL":
        score += 40

    # Long inactivity
    if stationary_time > 30:
        score += 20

    # Route deviation
    if route_deviation:
        score += 20

    # Abnormal speed
    if speed > 22.22:
        score += 15

    # Night movement
    if night_movement:
        score += 10

    # Maximum score
    score = min(score, 100)

    # Risk level
    if score <= 30:
        risk_level = "LOW"
    elif score <= 60:
        risk_level = "MEDIUM"
    elif score <= 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return {
        "risk_score": score,
        "risk_level": risk_level
    }
