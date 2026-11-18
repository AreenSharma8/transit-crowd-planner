"""Illustrative route options. Replace with verified GTFS routes/shapes before claiming live routing."""

NETWORK = [
    {"id": "sample-a", "label": "Sample route A", "route_key": "SAMPLE-A", "color": "#138a78", "travel_minutes": 36, "walk_minutes": 10, "transfers": 0, "boarding_stop": "Near your origin", "alighting_stop": "Near your destination", "stops": ["Origin area", "Central interchange", "Destination area"], "note": "Direct · illustrative route"},
    {"id": "sample-b", "label": "Sample route B + C", "route_key": "SAMPLE-B", "second_route_key": "SAMPLE-C", "color": "#d48a36", "travel_minutes": 42, "walk_minutes": 6, "transfers": 1, "boarding_stop": "Near your origin", "alighting_stop": "Near your destination", "transfer_stop": "Central interchange", "stops": ["Origin area", "Central interchange", "Destination area"], "note": "One transfer · illustrative route"},
    {"id": "sample-c", "label": "Sample route D", "route_key": "SAMPLE-D", "color": "#5368b5", "travel_minutes": 49, "walk_minutes": 4, "transfers": 0, "boarding_stop": "Near your origin", "alighting_stop": "Near your destination", "stops": ["Origin area", "Market junction", "Destination area"], "note": "Less walking · illustrative route"},
]


def make_options(origin: str, destination: str, depart: str, crowding_fn):
    """Return a usable demo itinerary; this is not a GTFS pathfinder."""
    options = []
    for route in NETWORK:
        signals = [crowding_fn(route["route_key"], depart)]
        route_names = [route["label"]]
        if route.get("second_route_key"):
            signals.append(crowding_fn(route["second_route_key"], depart))
            route_names = ["Sample route B", "Sample route C"]
        avg_score = round(sum(s["score"] for s in signals) / len(signals))
        avg_records = min(s["records"] for s in signals)
        confidence_rank = {"low": 0, "medium": 1, "high": 2}
        confidence = min((s["confidence"] for s in signals), key=lambda x: confidence_rank[x])
        total = route["travel_minutes"] + route["walk_minutes"]
        options.append({
            "id": route["id"], "label": route["label"], "route_names": route_names, "color": route["color"],
            "travel_minutes": route["travel_minutes"], "walk_minutes": route["walk_minutes"],
            "transfers": route["transfers"], "total_minutes": total,
            "boarding_stop": route["boarding_stop"], "alighting_stop": route["alighting_stop"],
            "transfer_stop": route.get("transfer_stop"),
            "stops": [origin, *route["stops"][1:-1], destination], "note": route["note"],
            "crowding": {"score": avg_score, "label": crowd_label(avg_score) if avg_records else "No matching samples", "confidence": confidence,
                         "records": avg_records, "signals": signals,
                         "basis": "Relative ticketing-activity index; not passenger occupancy."},
            "data_mode": "illustrative demo network",
        })
    return sorted(options, key=lambda x: (x["total_minutes"], x["crowding"]["score"]))


def crowd_label(score: int) -> str:
    if score < 30: return "Lighter signal"
    if score < 58: return "Moderate signal"
    if score < 78: return "Busy signal"
    return "High activity"
