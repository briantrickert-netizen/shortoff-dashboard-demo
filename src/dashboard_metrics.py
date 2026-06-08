import pandas as pd


def money(value: float) -> str:
    if pd.isna(value):
        value = 0
    return f"${value:,.0f}"


def percent(value: float) -> str:
    if pd.isna(value):
        value = 0
    return f"{value:.1%}"


def reservation_metrics(reservations: pd.DataFrame) -> dict:
    if reservations.empty:
        return {
            "gross_revenue": 0,
            "net_revenue": 0,
            "nights": 0,
            "adr": 0,
            "direct_share": 0,
            "bookings": 0,
        }

    confirmed = reservations[reservations.get("status", "").astype(str).str.lower() != "cancelled"].copy()
    gross = pd.to_numeric(confirmed.get("gross_revenue", 0), errors="coerce").fillna(0).sum()
    fees = pd.to_numeric(confirmed.get("fees", 0), errors="coerce").fillna(0).sum()
    taxes = pd.to_numeric(confirmed.get("taxes", 0), errors="coerce").fillna(0).sum()
    nights = pd.to_numeric(confirmed.get("nights", 0), errors="coerce").fillna(0).sum()
    bookings = len(confirmed)
    direct = confirmed.get("channel", pd.Series(dtype=str)).astype(str).str.lower().eq("direct").sum()

    return {
        "gross_revenue": gross,
        "net_revenue": gross - fees - taxes,
        "nights": int(nights),
        "adr": gross / nights if nights else 0,
        "direct_share": direct / bookings if bookings else 0,
        "bookings": bookings,
    }


def web_metrics(web: pd.DataFrame) -> dict:
    if web.empty:
        return {"sessions": 0, "cta_clicks": 0, "inquiries": 0, "booking_starts": 0, "cta_rate": 0}

    sessions = pd.to_numeric(web.get("sessions", 0), errors="coerce").fillna(0).sum()
    cta = pd.to_numeric(web.get("booking_cta_clicks", 0), errors="coerce").fillna(0).sum()
    inquiries = pd.to_numeric(web.get("inquiries", 0), errors="coerce").fillna(0).sum()
    starts = pd.to_numeric(web.get("booking_starts", 0), errors="coerce").fillna(0).sum()
    return {
        "sessions": int(sessions),
        "cta_clicks": int(cta),
        "inquiries": int(inquiries),
        "booking_starts": int(starts),
        "cta_rate": cta / sessions if sessions else 0,
    }


def review_metrics(reviews: pd.DataFrame) -> dict:
    if reviews.empty:
        return {"average_rating": 0, "review_count": 0}
    ratings = pd.to_numeric(reviews.get("rating", 0), errors="coerce").dropna()
    return {
        "average_rating": ratings.mean() if not ratings.empty else 0,
        "review_count": len(ratings),
    }
