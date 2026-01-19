import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_aadhaar_data

st.set_page_config(page_title="District Drilldown", layout="wide", initial_sidebar_state="expanded")


def alt_dark_chart(chart: alt.Chart) -> alt.Chart:
    return (
        chart
        .configure_view(stroke=None)
        .configure_axis(labelColor='#1f2937', titleColor='#1f4ed8')
        .configure_title(color='#1f4ed8')
        .configure_legend(labelColor='#1f2937', titleColor='#1f4ed8')
    )


def enrolment_district_tab(df, state, district):
    filtered = df[(df['state'] == state) & (df['district'] == district)]
    state_df = df[df['state'] == state]

    district_total = int(filtered['total_enrolments'].sum())
    state_total = int(state_df['total_enrolments'].sum())
    state_child_pct = (state_df['age_0_5'].sum() + state_df['age_5_17'].sum()) / state_total * 100 if state_total else 0
    district_child_pct = (filtered['age_0_5'].sum() + filtered['age_5_17'].sum()) / district_total * 100 if district_total else 0   
    col1, col2, col3 = st.columns(3)
    col1.metric('Total Enrolments', f"{district_total:,}")
    col2.metric('District Share of State Enrolments', f"{district_total / state_total * 100 if state_total else 0:.2f}%")
    col3.metric('Child Share (0–17)', f"{district_child_pct:.2f}%")
    if district_child_pct < state_child_pct:
        st.warning("District child enrolment share is below state average.")
    else:
        st.success("District child enrolment share meets or exceeds state average.")
    # Trend: district vs state average
    # Aggregate by month for cleaner, less cluttered chart
    state_daily = state_df.groupby(['date', 'district'])['total_enrolments'].sum().reset_index()
    state_daily['month'] = state_daily['date'].dt.to_period('M')
    state_level = (
        state_daily.groupby('month')['total_enrolments']
        .mean()
        .reset_index()
        .rename(columns={'total_enrolments': 'state_avg'})
    )
    state_level['date'] = state_level['month'].dt.to_timestamp()

    district_daily = filtered.groupby('date')['total_enrolments'].sum().reset_index()
    district_daily['month'] = district_daily['date'].dt.to_period('M')
    district_trend = (
        district_daily.groupby('month')['total_enrolments']
        .sum()
        .reset_index()
        .rename(columns={'total_enrolments': 'district_total'})
    )
    district_trend['date'] = district_trend['month'].dt.to_timestamp()

    trend_df = (
        pd.merge(state_level[['date', 'state_avg']], district_trend[['date', 'district_total']], on='date', how='outer')
        .melt(id_vars=['date'], value_vars=['state_avg', 'district_total'], var_name='series', value_name='value')
        .sort_values('date')
    )
    trend_df['month_name'] = trend_df['date'].dt.strftime('%b %Y')

    line = (
        alt.Chart(trend_df)
        .mark_line(point=True)
        .encode(
            x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')),
            y=alt.Y('value:Q', title='Total Enrolments'),
            color=alt.Color('series:N', title='Series'),
            tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('series:N'), alt.Tooltip('value:Q', format=',')]
        )
        .properties(height=320, title='Enrolment Trend: District vs State Average')
    )

    st.altair_chart(alt_dark_chart(line), use_container_width=True)

    # Month-on-month growth
    district_monthly = district_trend.set_index('date')['district_total'].pct_change().dropna()
    state_monthly = state_level.set_index('date')['state_avg'].pct_change().dropna()
    latest_growth = district_monthly.iloc[-1] if len(district_monthly) else 0
    state_latest = state_monthly.iloc[-1] if len(state_monthly) else 0

    col4, col5 = st.columns(2)
    col4.metric('Latest District MoM Growth', f"{latest_growth:.2%}")
    col5.metric('Latest State MoM Growth', f"{state_latest:.2%}")

    if latest_growth < state_latest:
        st.warning('District growth is lagging state trend.')
    else:
            st.success('District growth is keeping pace with or exceeding state trend.')

    # Pincode contribution
    st.divider()
    st.subheader('Pincodes Contribution within District')
    pincodes = (
        filtered.groupby('pincode')['total_enrolments']
        .sum()
        .reset_index()
        .sort_values('total_enrolments', ascending=False)
    )

    pincodes['pincode'] = pincodes['pincode'].astype(str)
    chart = (
        alt.Chart(pincodes.head(10))
        .mark_bar(color='#1f4ed8')
        .encode(
            x=alt.X('total_enrolments:Q', title='Total Enrolments'),
            y=alt.Y('pincode:N', sort='-x', title='Pincode'),
            tooltip=[alt.Tooltip('pincode:N'), alt.Tooltip('total_enrolments:Q', format=',')]
        )
        .properties(height=360, title='Top 10 Pincodes by Enrolments')
    )

    st.altair_chart(alt_dark_chart(chart), use_container_width=True)
    col1 , col2 = st.columns(2)
    top_pincode_share = pincodes.head(3)['total_enrolments'].sum() / district_total * 100 if district_total else 0
    col1.metric('Top 3 Pincodes Contribution', f"{top_pincode_share:.2f}%")

    low_activity_pincodes = pincodes[pincodes['total_enrolments'] < 0.01 * district_total]
    col2.metric('Low-Activity Pincodes', len(low_activity_pincodes))
    if top_pincode_share > 50 and len(pincodes)>5:
            st.warning('Enrolments are highly concentrated in a few pincodes.')
    # Age-wise distribution
    st.divider()
    st.subheader('Age Group Distribution')
    age_totals = filtered[['age_0_5', 'age_5_17', 'age_18_greater']].sum().reset_index()
    age_totals.columns = ['age_group', 'enrolments']
    age_totals["age_group"] = age_totals["age_group"].replace({
            "age_0_5": "0–5 Years",
            "age_5_17": "5–17 Years",
            "age_18_greater": "18+ Years"
        })
    age_chart = (
        alt.Chart(age_totals)
        .mark_bar(color='#1f4ed8')
        .encode(x=alt.X('age_group:N', title='Age Group', sort=['0–5 Years', '5–17 Years', '18+ Years']), y=alt.Y('enrolments:Q', title='Enrolments'), tooltip=[alt.Tooltip('enrolments:Q', format=',')])
        .properties(height=280, title='Enrolments by Age Group')
    )

    st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)

    st.divider()
    st.subheader('Day-of-week Distribution')
    filtered['day_of_week'] = filtered['date'].dt.dayofweek
    age_long = filtered.melt(id_vars=['date', 'day_of_week'], value_vars=['age_0_5', 'age_5_17', 'age_18_greater'], var_name='age_group', value_name='enrolments')
    dow = age_long.groupby(['day_of_week', 'age_group'])['enrolments'].sum().reset_index()
    day_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    dow["day_name"] = dow["day_of_week"].map(day_map)
    dow["day_name"] = pd.Categorical(
    dow["day_name"],
    categories=[
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ],
        ordered=True
    )

    dow_chart = (
    alt.Chart(dow)
    .mark_bar()
    .encode(
        x=alt.X("day_name:N", title="Day of Week", sort=list(dow["day_name"].cat.categories)),
        y=alt.Y("enrolments:Q", title="Enrolments"),
        color=alt.Color("age_group:N", title="Age Group"),
        tooltip=[
            alt.Tooltip("day_name:N", title="Day"),
            alt.Tooltip("age_group:N", title="Age Group"),
            alt.Tooltip("enrolments:Q", title="Enrolments", format=",")
        ]
        )
        .properties(height=320, title="Enrolments by Day of Week and Age Group")
    )

    st.altair_chart(alt_dark_chart(dow_chart), use_container_width=True)


    peak_day = age_long.groupby('day_of_week')['enrolments'].sum().idxmax()
    st.info(
    f"Highest enrolment activity observed on "
    f"{['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][peak_day]}."
    )
    st.caption(
        "Day-of-week analysis helps optimize staffing and mobile unit deployment. "
        "Peak activity days may require additional capacity to reduce wait times."
    )

    

def demographic_district_tab(df_demo, state, district):
    st.header('Demographic Updates — District Drilldown')
    filtered = df_demo[(df_demo['state'] == state) & (df_demo['district'] == district)]
    state_demo = df_demo[df_demo['state'] == state]

    total_updates = int(filtered['total_updates'].sum())
    col1 , col2 = st.columns(2)
    col1.metric('Total Demographic Updates', f"{total_updates:,}")

    state_total = int(state_demo['total_updates'].sum())
    col2.metric('District Share of State', f"{total_updates / state_total * 100 if state_total else 0:.2f}%")

    # Trend: Aggregate by month for cleaner, less cluttered chart
    state_daily = state_demo.groupby(['date', 'district'])[['demo_age_5_17', 'demo_age_17_']].sum()
    state_daily = state_daily.assign(total=lambda x: x.sum(axis=1)).reset_index()
    state_daily['month'] = state_daily['date'].dt.to_period('M')
    state_level = (
        state_daily.groupby('month')['total']
        .mean()
        .reset_index()
        .rename(columns={'total': 'state_avg'})
    )
    state_level['date'] = state_level['month'].dt.to_timestamp()

    district_daily = filtered.groupby('date')[['demo_age_5_17', 'demo_age_17_']].sum()
    district_daily = district_daily.assign(total=lambda x: x.sum(axis=1)).reset_index()
    district_daily['month'] = district_daily['date'].dt.to_period('M')
    district_trend = (
        district_daily.groupby('month')['total']
        .sum()
        .reset_index()
        .rename(columns={'total': 'district_total'})
    )
    district_trend['date'] = district_trend['month'].dt.to_timestamp()

    trend_df = (
        pd.merge(state_level[['date', 'state_avg']], district_trend[['date', 'district_total']], on='date', how='outer')
        .melt(id_vars=['date'], value_vars=['state_avg', 'district_total'], var_name='series', value_name='value')
        .sort_values('date')
    )
    trend_df['month_name'] = trend_df['date'].dt.strftime('%b %Y')

    line = (
        alt.Chart(trend_df)
        .mark_line(point=True)
        .encode(x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')), y=alt.Y('value:Q', title='Total Demographic Updates'), color=alt.Color('series:N', title='Series'), tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('series:N'), alt.Tooltip('value:Q', format=',')])
        .properties(height=320, title='Demographic Update Trend: District vs State Average')
    )
    st.altair_chart(alt_dark_chart(line), use_container_width=True)
    district_monthly = district_trend.set_index('date')['district_total'].pct_change().dropna()
    state_monthly = state_level.set_index('date')['state_avg'].pct_change().dropna()
    latest_growth = district_monthly.iloc[-1] if len(district_monthly) else 0
    state_latest = state_monthly.iloc[-1] if len(state_monthly) else 0

    col4, col5 = st.columns(2)
    col4.metric('Latest District MoM Growth', f"{latest_growth:.2%}")
    col5.metric('Latest State MoM Growth', f"{state_latest:.2%}")

    if latest_growth < state_latest:
        st.warning('District growth is lagging state trend.')
    else:
            st.success('District growth is keeping pace with or exceeding state trend.')
    # Pincode contribution
    st.divider()
    st.subheader('Top Pincodes by Demographic Updates')
    pincodes = (
        filtered.groupby('pincode')[['demo_age_5_17', 'demo_age_17_']]
        .sum()
        .assign(total=lambda x: x.sum(axis=1))
        .reset_index()
        .sort_values('total', ascending=False)
    )
    pincodes['pincode'] = pincodes['pincode'].astype(str)

    chart = (
        alt.Chart(pincodes.head(10))
        .mark_bar(color='#1f4ed8')
        .encode(x=alt.X('total:Q', title='Total Updates'), y=alt.Y('pincode:N', sort='-x', title='Pincode'), tooltip=[alt.Tooltip('pincode:N'), alt.Tooltip('total:Q', format=',')])
        .properties(height=360, title = 'Top 10 pincodes by Demographic Updates')
    )
    st.altair_chart(alt_dark_chart(chart), use_container_width=True)
    col1, col2 = st.columns(2)
    top3_share = pincodes.head(3)['total'].sum() / total_updates * 100 if total_updates else 0
    col1.metric('Top 3 Pincodes Contribution', f"{top3_share:.2f}%")

    low_activity_pincodes = pincodes[pincodes['total'] < 0.01 * total_updates]
    col2.metric('Low-Activity Pincodes', len(low_activity_pincodes))
    if top3_share > 50 and len(pincodes)>5:
            st.warning('Demographic updates are highly concentrated in a few pincodes.')

    st.divider()
    st.subheader('Age Group Distribution')
    age_totals = filtered[['demo_age_5_17', 'demo_age_17_']].sum().reset_index()
    age_totals.columns = ['age_group', 'demographic_updates']
    age_totals["age_group"] = age_totals["age_group"].replace({
            "demo_age_5_17": "0–17 Years",
            "demo_age_17_": "18+ Years",
        })
    age_chart = (
        alt.Chart(age_totals)
        .mark_bar(color='#1f4ed8')
        .encode(x=alt.X('age_group:N', title='Age Group', sort=['0–17 Years', '18+ Years']), y=alt.Y('demographic_updates:Q', title='Demographic Updates'), tooltip=[alt.Tooltip('demographic_updates:Q', format=',')])
        .properties(height=280, title='Demographic Updates by Age Group')
    )

    st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)


    st.divider()
    st.subheader('Day-of-week Distribution')
    filtered['day_of_week'] = filtered['date'].dt.dayofweek
    age_long = filtered.melt(id_vars=['date', 'day_of_week'], value_vars=['demo_age_5_17', 'demo_age_17_'], var_name='age_group', value_name='demographic_updates')
    dow = age_long.groupby(['day_of_week', 'age_group'])['demographic_updates'].sum().reset_index()
    day_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    dow["day_name"] = dow["day_of_week"].map(day_map)
    dow["day_name"] = pd.Categorical(
    dow["day_name"],
    categories=[
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ],
        ordered=True
    )

    dow_chart = (
    alt.Chart(dow)
    .mark_bar()
    .encode(
        x=alt.X("day_name:N", title="Day of Week", sort=list(dow["day_name"].cat.categories)),
        y=alt.Y("demographic_updates:Q", title="Demographic Updates"),
        color=alt.Color("age_group:N", title="Age Group"),
        tooltip=[
            alt.Tooltip("day_name:N", title="Day"),
            alt.Tooltip("age_group:N", title="Age Group"),
            alt.Tooltip("demographic_updates:Q", title="Demographic Updates", format=",")
        ]
        )
        .properties(height=320, title="Demographic Updates by Day of Week and Age Group")
    )

    st.altair_chart(alt_dark_chart(dow_chart), use_container_width=True)


    peak_day = age_long.groupby('day_of_week')['demographic_updates'].sum().idxmax()
    st.info(
    f"Highest update activity observed on "
    f"{['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][peak_day]}."
    )
    st.caption(
        "Day-of-week analysis helps optimize staffing and mobile unit deployment. "
        "Peak activity days may require additional capacity to reduce wait times."
    )


def biometric_district_tab(df_bio, state, district):
    st.header('Biometric Updates — District Drilldown')
    filtered = df_bio[(df_bio['state'] == state) & (df_bio['district'] == district)]
    total_updates = int(filtered[['bio_age_5_17', 'bio_age_17_']].sum().sum())
    state_bio = df_bio[df_bio['state'] == state]
    col1, col2 = st.columns(2)
    col1.metric('Total Biometric Updates', f"{total_updates:,}")
    state_total = int(state_bio['total_updates'].sum())
    col2.metric('District Share of State', f"{total_updates / state_total * 100 if state_total else 0:.2f}%")
    # Trend: Aggregate by month for cleaner, less cluttered chart
    state_daily = df_bio[df_bio['state'] == state].groupby(['date', 'district'])[['bio_age_5_17', 'bio_age_17_']].sum()
    state_daily = state_daily.assign(total=lambda x: x.sum(axis=1)).reset_index()
    state_daily['month'] = state_daily['date'].dt.to_period('M')
    state_level = (
        state_daily.groupby('month')['total']
        .mean()
        .reset_index()
        .rename(columns={'total': 'state_avg'})
    )
    state_level['date'] = state_level['month'].dt.to_timestamp()

    district_daily = filtered.groupby('date')[['bio_age_5_17', 'bio_age_17_']].sum()
    district_daily = district_daily.assign(total=lambda x: x.sum(axis=1)).reset_index()
    district_daily['month'] = district_daily['date'].dt.to_period('M')
    district_trend = (
        district_daily.groupby('month')['total']
        .sum()
        .reset_index()
        .rename(columns={'total': 'district_total'})
    )
    district_trend['date'] = district_trend['month'].dt.to_timestamp()

    trend_df = (
        pd.merge(state_level[['date', 'state_avg']], district_trend[['date', 'district_total']], on='date', how='outer')
        .melt(id_vars=['date'], value_vars=['state_avg', 'district_total'], var_name='series', value_name='value')
        .sort_values('date')
    )
    trend_df['month_name'] = trend_df['date'].dt.strftime('%b %Y')

    line = (
        alt.Chart(trend_df)
        .mark_line(point=True)
        .encode(x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')), y=alt.Y('value:Q', title='Total Biometric Updates'), color=alt.Color('series:N', title='Series'), tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('series:N'), alt.Tooltip('value:Q', format=',')])
        .properties(height=320, title='Biometric Update Trend: District vs State Average')
    )
    st.altair_chart(alt_dark_chart(line), use_container_width=True)
    district_monthly = district_trend.set_index('date')['district_total'].pct_change().dropna()
    state_monthly = state_level.set_index('date')['state_avg'].pct_change().dropna()
    latest_growth = district_monthly.iloc[-1] if len(district_monthly) else 0
    state_latest = state_monthly.iloc[-1] if len(state_monthly) else 0

    col4, col5 = st.columns(2)
    col4.metric('Latest District MoM Growth', f"{latest_growth:.2%}")
    col5.metric('Latest State MoM Growth', f"{state_latest:.2%}")

    if latest_growth < state_latest:
        st.warning('District growth is lagging state trend.')
    else:
            st.success('District growth is keeping pace with or exceeding state trend.')
    # Pincode contribution
    st.divider()
    st.subheader('Pincode Contribution within District')
    pincodes = (
        filtered.groupby('pincode')[['bio_age_5_17', 'bio_age_17_']]
        .sum()
        .assign(total=lambda x: x.sum(axis=1))
        .reset_index()
        .sort_values('total', ascending=False)
    )
    pincodes['pincode'] = pincodes['pincode'].astype(str)

    chart = (
        alt.Chart(pincodes.head(10))
        .mark_bar(color='#1f4ed8')
        .encode(x=alt.X('total:Q', title='Total Updates'), y=alt.Y('pincode:N', sort='-x', title='Pincode'), tooltip=[alt.Tooltip('pincode:N'), alt.Tooltip('total:Q', format=',')])
        .properties(height=360, title='Top 10 pincodes by Biometric Updates')
    )
    st.altair_chart(alt_dark_chart(chart), use_container_width=True)
    top3_share = pincodes.head(3)['total'].sum() / total_updates * 100 if total_updates else 0
    col1 , col2 = st.columns(2)
    col1.metric('Top 3 Pincodes Contribution', f"{top3_share:.2f}%")

    low_activity_pincodes = pincodes[pincodes['total'] < 0.01 * total_updates]
    col2.metric('Low-Activity Pincodes', len(low_activity_pincodes))
    if top3_share > 50 and len(pincodes)>5:
            st.warning('Biometric updates are highly concentrated in a few pincodes.')
    st.divider()
    st.subheader('Age Group Distribution')
    age_totals = filtered[['bio_age_5_17', 'bio_age_17_']].sum().reset_index()
    age_totals.columns = ['age_group', 'biometric_updates']
    age_totals["age_group"] = age_totals["age_group"].replace({
            "bio_age_5_17": "0–17 Years",
            "bio_age_17_": "18+ Years",
        })
    age_chart = (
        alt.Chart(age_totals)
        .mark_bar(color='#1f4ed8')
        .encode(x=alt.X('age_group:N', title='Age Group', sort=['0–17 Years', '18+ Years']), y=alt.Y('biometric_updates:Q', title='Biometric Updates'), tooltip=[alt.Tooltip('biometric_updates:Q', format=',')])
        .properties(height=280, title='Biometric Updates by Age Group')
    )

    st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)
    st.divider()
    st.subheader('Day-of-week Distribution')
    filtered['day_of_week'] = filtered['date'].dt.dayofweek
    age_long = filtered.melt(id_vars=['date', 'day_of_week'], value_vars=['bio_age_5_17', 'bio_age_17_'], var_name='age_group', value_name='biometric_updates')
    dow = age_long.groupby(['day_of_week', 'age_group'])['biometric_updates'].sum().reset_index()
    day_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    dow["day_name"] = dow["day_of_week"].map(day_map)
    dow["day_name"] = pd.Categorical(
    dow["day_name"],
    categories=[
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ],
        ordered=True
    )

    dow_chart = (
    alt.Chart(dow)
    .mark_bar()
    .encode(
        x=alt.X("day_name:N", title="Day of Week", sort=list(dow["day_name"].cat.categories)),
        y=alt.Y("biometric_updates:Q", title="Biometric Updates"),
        color=alt.Color("age_group:N", title="Age Group"),
        tooltip=[
            alt.Tooltip("day_name:N", title="Day"),
            alt.Tooltip("age_group:N", title="Age Group"),
            alt.Tooltip("biometric_updates:Q", title="Biometric Updates", format=",")
        ]
        )
        .properties(height=320, title="Biometric Updates by Day of Week and Age Group")
    )

    st.altair_chart(alt_dark_chart(dow_chart), use_container_width=True)


    peak_day = age_long.groupby('day_of_week')['biometric_updates'].sum().idxmax()
    st.info(
    f"Highest update activity observed on "
    f"{['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][peak_day]}."
    )
    st.caption(
        "Day-of-week analysis helps optimize staffing and mobile unit deployment. "
        "Peak activity days may require additional capacity to reduce wait times."
    )

def main():
    st.title('District Drilldown')
    st.divider()

    try:
        df, df_demo, df_bio = load_aadhaar_data()
    except Exception as e:
        st.error(f'Failed to load data: {e}')
        return

    # Common sidebar filters
    st.sidebar.header('Filters')
    state = st.sidebar.selectbox('State', sorted(df['state'].unique()), index=0)
    district = st.sidebar.selectbox('District', sorted(df[df['state'] == state]['district'].unique()), index=0)

    tabs = st.tabs(['Enrolment', 'Demographic Updates', 'Biometric Updates'])

    with tabs[0]:
        enrolment_district_tab(df, state, district)

    with tabs[1]:
        demographic_district_tab(df_demo, state, district)

    with tabs[2]:
        biometric_district_tab(df_bio, state, district)


if __name__ == '__main__':
    main()
