def pick(ch: dict) -> dict:
    team = ch.get("team_size", 3)
    horizon = ch.get("delivery_horizon_days", 30)
    pref = ch.get("preferred_methodology", "auto")
    if pref != "auto":
        chosen = pref
    elif team <= 4 and horizon < 21:
        chosen = "kanban"
    elif horizon >= 21:
        chosen = "scrum"
    else:
        chosen = "hybrid"
    return {"chosen": chosen, "rationale": f"team={team}, horizon={horizon}, pref={pref}"}
