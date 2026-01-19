import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_aadhaar_data

st.set_page_config(page_title="Overview", layout="wide", initial_sidebar_state="expanded")


def alt_dark_chart(chart: alt.Chart) -> alt.Chart:
    return (
        chart
        .configure_view(stroke=None)
        .configure_axis(labelColor='#1f2937', titleColor='#1f4ed8')
        .configure_title(color='#1f4ed8')
        .configure_legend(labelColor='#1f2937', titleColor='#1f4ed8')
    )


def _format_period_label(p):
    try:
        return p.to_timestamp().strftime("%b %Y")
    except Exception:
        return str(p)


def render_enrolment_tab(df):
    st.header('Enrolment — Snapshot')
    total = int(df['total_enrolments'].sum())
    children_pct = (df['age_0_5'].sum() + df['age_5_17'].sum()) / total * 100 if total else 0
    adult_pct = df['age_18_greater'].sum() / total * 100 if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric('Total Enrolments', f"{total:,}")
    c2.metric('Children Coverage (0–17)', f"{children_pct:.2f}%")
    c3.metric('Adult Coverage (18+)', f"{adult_pct:.2f}%")

    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month')['total_enrolments'].sum()

    monthly_df = monthly.reset_index()
    monthly_df['date'] = monthly_df['month'].dt.to_timestamp()
    monthly_df['month_name'] = monthly_df['date'].dt.strftime('%b %Y')
    
    monthly_growth = monthly.pct_change() * 100
    latest_growth = monthly_growth.iloc[-1]
    col1, col2 = st.columns([1, 2])
    col1.metric(
        "Latest National MoM Growth",
        f"{latest_growth:.2f}%",
    )
    if latest_growth < 0:
        col2.error("Enrolments declined in the latest month. Immediate review recommended.")
    elif latest_growth < 2:
        col2.warning("Enrolment growth is slowing. Close monitoring advised.")
    else:
        col2.success("Healthy enrolment growth observed.")
    
    trend_chart = (
        alt.Chart(monthly_df)
        .mark_line(point=True, color='#1f4ed8')
        .encode(x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')), y=alt.Y('total_enrolments:Q', title='Total Enrolments'), tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('total_enrolments:Q', format=',')])
        .properties(height=300, title="Enrolment Trend")
    )
    st.altair_chart(alt_dark_chart(trend_chart), use_container_width=True)

    # Top states
    st.subheader('Geographic Distribution')
    state_enrolments = df.groupby('state', as_index=False)['total_enrolments'].sum().sort_values('total_enrolments', ascending=False)

    max_state = state_enrolments.iloc[0]
    min_state = state_enrolments.iloc[-1]

    col1, col2 = st.columns(2)
    col1.metric(
    "State with Maximum Enrolments",
    max_state['state'],
    f"{max_state['total_enrolments']:,}"
    )

    col2.metric(
    "State with Minimum Enrolments",
    min_state['state'],
    f"{min_state['total_enrolments']:,}"
    )


    state_chart = (
        alt.Chart(state_enrolments.head(10))
        .mark_bar(color='#1f4ed8')
        .encode(x=alt.X('total_enrolments:Q', title='Total Enrolments'), y=alt.Y('state:N', sort='-x', title='State'), tooltip=[alt.Tooltip('state:N'), alt.Tooltip('total_enrolments:Q', format=',')])
        .properties(height=320,title="Top 10 States by Total Enrolment")
    )
    st.altair_chart(alt_dark_chart(state_chart), use_container_width=True)

    st.subheader('Age Group Distribution')
    age_totals = df[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
    age_df = (
        age_totals
        .reset_index()
        .rename(columns={"index": "age_group", 0: "total"})
    )
    age_df["age_group"] = age_df["age_group"].replace({
        "age_0_5": "0–5 Years",
        "age_5_17": "5–17 Years",
        "age_18_greater": "18+ Years"
    })
    national_child_avg = (age_df[age_df['age_group'].isin(['0–5 Years', '5–17 Years'])]['total'].sum() / age_df['total'].sum()) * 100 if age_df['total'].sum() else 0
    st.metric(
        label="Average Child Enrolment Share (0–17 years)", 
        value=f"{round(national_child_avg, 2)}%"
    )
    st.caption(
        "The average child enrolment share serves as a benchmark to evaluate "
        "state-level performance. States below this benchmark may require targeted "
        "interventions to improve enrolment among children and adolescents."
    )
    age_chart = (
    alt.Chart(age_df)
        .mark_bar(color="#1f4ed8")
        .encode(
            x=alt.X("age_group:N", title="Age Group", sort=["0–5 Years", "5–17 Years", "18+ Years"]),
            y=alt.Y("total:Q", title="Total Enrolments"),
            tooltip=[
                alt.Tooltip("age_group:N", title="Age Group"),
                alt.Tooltip("total:Q", title="Total", format=",")
            ]
        )
        .properties(height=300, title="Enrolments by Age Group")
    )

    st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)


def render_demo_tab(df_demo):
    st.header('Demographic Updates — Snapshot')
    total_updates = int(df_demo[['demo_age_5_17', 'demo_age_17_']].sum().sum())
    child_pct = df_demo['demo_age_5_17'].sum() / total_updates * 100 if total_updates else 0
    adult_pct = df_demo['demo_age_17_'].sum() / total_updates * 100 if total_updates else 0

    c1, c2, c3 = st.columns(3)
    c1.metric('Total Demographic Updates', f"{total_updates:,}")
    c2.metric('Child / Adolescent (5–17)', f"{child_pct:.2f}%")
    c3.metric('Adult (18+)', f"{adult_pct:.2f}%")

    df_demo['month'] = df_demo['date'].dt.to_period('M')
    monthly_updates = df_demo.groupby('month')[['demo_age_5_17', 'demo_age_17_']].sum()
    monthly_updates['total_updates'] = monthly_updates.sum(axis=1)

    monthly_df = monthly_updates.reset_index()
    monthly_df['date'] = monthly_df['month'].dt.to_timestamp()
    monthly_df['month_name'] = monthly_df['date'].dt.strftime('%b %Y')
    monthly_growth = monthly_updates['total_updates'].pct_change() * 100
    latest_growth = monthly_growth.iloc[-1]
    col1, col2 = st.columns([1, 2])
    col1.metric(
        "Latest National MoM Growth",
        f"{latest_growth:.2f}%",
    )
    if latest_growth < 0:
        col2.error("Updates declined in the latest month. Immediate review recommended.")
    elif latest_growth < 2:
        col2.warning("Update growth is slowing. Close monitoring advised.")
    else:
        col2.success("Healthy update growth observed.")
    trend_chart = (
        alt.Chart(monthly_df)
        .mark_line(point=True, color='#1f4ed8')
        .encode(x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')), y=alt.Y('total_updates:Q', title='Total Demographic Updates'), tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('total_updates:Q', format=',')])
        .properties(height=300, title="Demographic Updates Trend")
    )
    st.altair_chart(alt_dark_chart(trend_chart), use_container_width=True)
    st.subheader('Geographic Distribution')
    state_updates = df_demo.groupby('state')[['demo_age_5_17', 'demo_age_17_']].sum().assign(total_updates=lambda x: x.sum(axis=1)).reset_index().sort_values('total_updates', ascending=False)
    max_state = state_updates.iloc[0]
    min_state = state_updates.iloc[-1]

    col1, col2 = st.columns(2)
    col1.metric(
    "State with Maximum Demographic Updates",
    max_state['state'],
    f"{max_state['total_updates']:,}"
    )

    col2.metric(
        "State with Minimum Demographic Updates",
        min_state['state'],
        f"{min_state['total_updates']:,}"
    )
    state_chart = (
        alt.Chart(state_updates.head(10))
        .mark_bar(color='#1f4ed8')
        .encode(x=alt.X('total_updates:Q', title='Total Updates'), y=alt.Y('state:N', sort='-x', title='State'), tooltip=[alt.Tooltip('state:N'), alt.Tooltip('total_updates:Q', format=',')])
        .properties(height=320, title = "Top 10 States by Demographic Updates")
    )
    st.altair_chart(alt_dark_chart(state_chart), use_container_width=True)

    st.subheader('Age Group Distribution')
    age_totals = df_demo[['demo_age_5_17', 'demo_age_17_']].sum()
    age_df = (
        age_totals
        .reset_index()
        .rename(columns={"index": "age_group", 0: "total"})
    )
    age_df["age_group"] = age_df["age_group"].replace({
        "demo_age_5_17": "5–17 Years",
        "demo_age_17_": "18+ Years"
    })
    age_chart = (
    alt.Chart(age_df)
        .mark_bar(color="#1f4ed8")
        .encode(
            x=alt.X("age_group:N", title="Age Group", sort=["5–17 Years", "18+ Years"]),
            y=alt.Y("total:Q", title="Total Updates"),
            tooltip=[
                alt.Tooltip("age_group:N", title="Age Group"),
                alt.Tooltip("total:Q", title="Total", format=",")
            ]
        )
        .properties(height=300, title="Demographic Updates by Age Group")
    )

    st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)


def render_bio_tab(df_bio):
    st.header('Biometric Updates — Snapshot')
    total_updates = int(df_bio[['bio_age_5_17', 'bio_age_17_']].sum().sum())
    child_pct = df_bio['bio_age_5_17'].sum() / total_updates * 100 if total_updates else 0
    adult_pct = df_bio['bio_age_17_'].sum() / total_updates * 100 if total_updates else 0

    c1, c2, c3 = st.columns(3)
    c1.metric('Total Biometric Updates', f"{total_updates:,}")
    c2.metric('Child / Adolescent (5–17)', f"{child_pct:.2f}%")
    c3.metric('Adult (18+)', f"{adult_pct:.2f}%")

    df_bio['month'] = df_bio['date'].dt.to_period('M')
    monthly = df_bio.groupby('month')[['bio_age_5_17', 'bio_age_17_']].sum()
    monthly['total_updates'] = monthly.sum(axis=1)

    monthly_df = monthly.reset_index()
    monthly_df['date'] = monthly_df['month'].dt.to_timestamp()
    monthly_df['month_name'] = monthly_df['date'].dt.strftime('%b %Y')
    monthly_growth = monthly['total_updates'].pct_change() * 100
    latest_growth = monthly_growth.iloc[-1]
    col1, col2 = st.columns([1, 2])
    col1.metric(
        "Latest National MoM Growth",
        f"{latest_growth:.2f}%",
    )
    if latest_growth < 0:
        col2.error("Updates declined in the latest month. Immediate review recommended.")
    elif latest_growth < 2:
        col2.warning("Update growth is slowing. Close monitoring advised.")
    else:
        col2.success("Healthy update growth observed.")
    trend_chart = (
        alt.Chart(monthly_df)
        .mark_line(point=True, color='#1f4ed8')
        .encode(x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')), y=alt.Y('total_updates:Q', title='Total Biometric Updates'), tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('total_updates:Q', format=',')])
        .properties(height=300,title="Biometric Updates Trend")
    )
    st.altair_chart(alt_dark_chart(trend_chart), use_container_width=True)

    state_updates = df_bio.groupby('state')[['bio_age_5_17', 'bio_age_17_']].sum().assign(total_updates=lambda x: x.sum(axis=1)).reset_index().sort_values('total_updates', ascending=False)
    st.subheader('Geographic Distribution')
    max_state = state_updates.iloc[0]
    min_state = state_updates.iloc[-1]

    col1, col2 = st.columns(2)
    col1.metric(
    "State with Maximum Biometric Updates",
    max_state['state'],
    f"{max_state['total_updates']:,}"
    )
    col2.metric(
        "State with Minimum Biometric Updates",
        min_state['state'],
        f"{min_state['total_updates']:,}"
    )
    state_chart = (
        alt.Chart(state_updates.head(10))
        .mark_bar(color='#1f4ed8')
        .encode(x=alt.X('total_updates:Q', title='Total Updates'), y=alt.Y('state:N', sort='-x', title='State'), tooltip=[alt.Tooltip('state:N'), alt.Tooltip('total_updates:Q', format=',')])
        .properties(height=320,title="Top 10 States by Biometric Updates")
    )
    st.altair_chart(alt_dark_chart(state_chart), use_container_width=True)

    
    st.subheader('Age Group Distribution')
    age_totals = df_bio[['bio_age_5_17', 'bio_age_17_']].sum()
    age_df = (
        age_totals
        .reset_index()
        .rename(columns={"index": "age_group", 0: "total"})
    )
    age_df["age_group"] = age_df["age_group"].replace({
        "bio_age_5_17": "5–17 Years",
        "bio_age_17_": "18+ Years"
    })
    age_chart = (
    alt.Chart(age_df)
        .mark_bar(color="#1f4ed8")
        .encode(
            x=alt.X("age_group:N", title="Age Group", sort=["5–17 Years", "18+ Years"]),
            y=alt.Y("total:Q", title="Total Updates"),
            tooltip=[
                alt.Tooltip("age_group:N", title="Age Group"),
                alt.Tooltip("total:Q", title="Total", format=",")
            ]
        )
        .properties(height=300, title="Biometric Updates by Age Group")
    )

    st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)

def main():
    st.title('Overview')
    st.divider()
    # Altair-based dark styling applied via helper on charts

    try:
        df, df_demo, df_bio = load_aadhaar_data()
    except Exception as e:
        st.error(f'Failed to load data: {e}')
        return

    tabs = st.tabs(['Enrolment', 'Demographic Updates', 'Biometric Updates'])

    with tabs[0]:
        render_enrolment_tab(df)

    with tabs[1]:
        render_demo_tab(df_demo)

    with tabs[2]:
        render_bio_tab(df_bio)


if __name__ == '__main__':
    main()
