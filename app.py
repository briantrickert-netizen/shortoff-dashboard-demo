import pandas as pd
import streamlit as st

from src.dashboard_data import data_freshness, filter_by_date, load_table
from src.dashboard_metrics import money, percent, reservation_metrics, review_metrics, web_metrics


st.set_page_config(
    page_title="Shortoff Live Dashboard",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_all_tables():
    names = ["reservations", "web_analytics", "seo_queries", "reviews", "issues"]
    return {name: load_table(name) for name in names}


def source_badge(source: str) -> str:
    if source == "private":
        return "Private data"
    if source == "sample":
        return "Sample data"
    return "Missing"


tables = load_all_tables()
reservations, reservations_source = tables["reservations"]
web, web_source = tables["web_analytics"]
seo, seo_source = tables["seo_queries"]
reviews, reviews_source = tables["reviews"]
issues, issues_source = tables["issues"]

all_dates = []
for frame, column in [(reservations, "date_booked"), (web, "date"), (seo, "date"), (reviews, "date"), (issues, "date")]:
    if not frame.empty and column in frame.columns:
        all_dates.extend(frame[column].dropna().tolist())

default_start = min(all_dates).date() if all_dates else pd.Timestamp.today().date()
default_end = max(all_dates).date() if all_dates else pd.Timestamp.today().date()

with st.sidebar:
    st.title("Shortoff")
    st.caption("Private business dashboard")
    start_date, end_date = st.date_input(
        "Date range",
        value=(default_start, default_end),
        min_value=default_start,
        max_value=default_end,
    )
    target_direct_share = st.slider("Direct booking share target", 0, 100, 45, 5) / 100
    target_cta_rate = st.slider("Booking CTA click target", 0, 25, 8, 1) / 100
    st.divider()
    st.write("Data sources")
    for label, source in [
        ("Reservations", reservations_source),
        ("Web analytics", web_source),
        ("SEO queries", seo_source),
        ("Reviews", reviews_source),
        ("Issues", issues_source),
    ]:
        st.caption(f"{label}: {source_badge(source)}")


reservations_period = filter_by_date(reservations, "date_booked", start_date, end_date)
web_period = filter_by_date(web, "date", start_date, end_date)
seo_period = filter_by_date(seo, "date", start_date, end_date)
reviews_period = filter_by_date(reviews, "date", start_date, end_date)
issues_period = filter_by_date(issues, "date", start_date, end_date)

booking_stats = reservation_metrics(reservations_period)
traffic_stats = web_metrics(web_period)
guest_stats = review_metrics(reviews_period)

st.title("Shortoff Dashboard Demo")
st.caption("Public demo using sample booking, marketing, SEO, review, and operating data.")

st.info("Demo mode: all panels use sample data committed under data/sample/. Do not add real business exports to this public repo.")

metrics = st.columns(6)
metrics[0].metric("Gross revenue", money(booking_stats["gross_revenue"]))
metrics[1].metric("Net revenue", money(booking_stats["net_revenue"]))
metrics[2].metric("Booked nights", f"{booking_stats['nights']:,}")
metrics[3].metric("ADR", money(booking_stats["adr"]))
metrics[4].metric("Direct share", percent(booking_stats["direct_share"]), delta=percent(booking_stats["direct_share"] - target_direct_share))
metrics[5].metric("CTA rate", percent(traffic_stats["cta_rate"]), delta=percent(traffic_stats["cta_rate"] - target_cta_rate))

tab_snapshot, tab_bookings, tab_marketing, tab_guest, tab_health = st.tabs(
    ["Snapshot", "Bookings", "Marketing and SEO", "Guest Experience", "Data Health"]
)

with tab_snapshot:
    left, right = st.columns([1.15, 0.85])
    with left:
        st.subheader("Revenue by booking month")
        if not reservations_period.empty:
            monthly = reservations_period.copy()
            monthly["month"] = monthly["date_booked"].dt.to_period("M").dt.to_timestamp()
            chart = monthly.groupby("month", as_index=False)["gross_revenue"].sum().set_index("month")
            st.bar_chart(chart)
        else:
            st.warning("No reservation rows for this period.")
    with right:
        st.subheader("Open operating issues")
        if not issues_period.empty:
            open_issues = issues_period[issues_period["status"].astype(str).str.lower() != "closed"]
            st.dataframe(open_issues[["date", "area", "issue", "impact", "next_action"]], use_container_width=True, hide_index=True)
        else:
            st.warning("No issue rows for this period.")

with tab_bookings:
    left, right = st.columns(2)
    with left:
        st.subheader("Channel mix")
        if not reservations_period.empty:
            channel = reservations_period.groupby("channel", as_index=False)["gross_revenue"].sum().sort_values("gross_revenue", ascending=False)
            st.bar_chart(channel.set_index("channel"))
        else:
            st.warning("No reservation rows for this period.")
    with right:
        st.subheader("Reservations")
        st.dataframe(reservations_period, use_container_width=True, hide_index=True)

with tab_marketing:
    traffic_left, traffic_right = st.columns(2)
    with traffic_left:
        st.subheader("Traffic by source")
        if not web_period.empty:
            source = web_period.groupby("source", as_index=False)[["sessions", "booking_cta_clicks", "booking_starts"]].sum()
            st.dataframe(source, use_container_width=True, hide_index=True)
            st.bar_chart(source.set_index("source")[["sessions", "booking_cta_clicks"]])
        else:
            st.warning("No web analytics rows for this period.")
    with traffic_right:
        st.subheader("Top SEO queries")
        if not seo_period.empty:
            query = seo_period.groupby("query", as_index=False).agg(
                clicks=("clicks", "sum"),
                impressions=("impressions", "sum"),
                avg_position=("avg_position", "mean"),
            ).sort_values("clicks", ascending=False)
            st.dataframe(query.head(15), use_container_width=True, hide_index=True)
        else:
            st.warning("No SEO query rows for this period.")

with tab_guest:
    guest_left, guest_right = st.columns([0.75, 1.25])
    with guest_left:
        st.subheader("Review snapshot")
        st.metric("Average rating", f"{guest_stats['average_rating']:.2f}")
        st.metric("Reviews", f"{guest_stats['review_count']:,}")
    with guest_right:
        st.subheader("Review topics")
        if not reviews_period.empty:
            topics = reviews_period.groupby(["topic", "sentiment"], as_index=False).size().sort_values("size", ascending=False)
            st.dataframe(topics, use_container_width=True, hide_index=True)
        else:
            st.warning("No review rows for this period.")

with tab_health:
    st.subheader("Data freshness")
    freshness = pd.DataFrame(
        [
            {"table": "reservations", "source": source_badge(reservations_source), "latest_date": data_freshness(reservations, "date_booked")},
            {"table": "web_analytics", "source": source_badge(web_source), "latest_date": data_freshness(web, "date")},
            {"table": "seo_queries", "source": source_badge(seo_source), "latest_date": data_freshness(seo, "date")},
            {"table": "reviews", "source": source_badge(reviews_source), "latest_date": data_freshness(reviews, "date")},
            {"table": "issues", "source": source_badge(issues_source), "latest_date": data_freshness(issues, "date")},
        ]
    )
    st.dataframe(freshness, use_container_width=True, hide_index=True)

    st.subheader("Expected private CSV schemas")
    st.caption("Use these schemas in the private live dashboard repo, not this public demo.")
    st.code(
        """data/private/reservations.csv: date_booked, check_in, check_out, channel, gross_revenue, fees, taxes, nights, status
data/private/web_analytics.csv: date, source, sessions, booking_cta_clicks, inquiries, booking_starts
data/private/seo_queries.csv: date, query, landing_page, clicks, impressions, avg_position
data/private/reviews.csv: date, platform, rating, sentiment, topic
data/private/issues.csv: date, area, issue, impact, status, next_action""",
        language="text",
    )
