import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_aadhaar_data

st.set_page_config(page_title="State Drilldown", layout="wide", initial_sidebar_state="expanded")


def alt_dark_chart(chart: alt.Chart) -> alt.Chart:
    return (
        chart
        .configure_view(stroke=None)
        .configure_axis(labelColor='#1f2937', titleColor='#1f4ed8')
        .configure_title(color='#1f4ed8')
        .configure_legend(labelColor='#1f2937', titleColor='#1f4ed8')
    )


def enrolment_tab(df, selected_state=None):
    if selected_state:
        st.header(f"{selected_state} — Enrolment Drilldown")
        state_df = df[df['state'] == selected_state]

        # Snapshot metrics
        national_total = df['total_enrolments'].sum()
        state_total = state_df['total_enrolments'].sum()
        state_share_national = state_total / national_total * 100 if national_total else 0
        state_child_pct = (state_df['age_0_5'].sum() + state_df['age_5_17'].sum()) / state_total * 100 if state_total else 0
        national_child_pct = (df['age_0_5'].sum() + df['age_5_17'].sum()) / national_total * 100 if national_total else 0

        c1, c2, c3 = st.columns(3)
        c1.metric('Total Enrolments', f"{int(state_total):,}")
        c2.metric('State Share of National Enrolments', f"{state_share_national:.2f}%")
        c3.metric('Child Share (0–17)', f"{state_child_pct:.2f}%")

        if state_child_pct < national_child_pct:
            st.warning('State child enrolment share is below national average.')
        else:
            st.success('State child enrolment share meets or exceeds national average.')

        # Trend: state vs national
        state_df_trend = state_df.copy()
        state_df_trend['month'] = state_df_trend['date'].dt.to_period('M')
        df_trend = df.copy()
        df_trend['month'] = df_trend['date'].dt.to_period('M')
        
        national_trend = (
            df_trend.groupby(['month', 'state'])['total_enrolments']
            .sum()
            .groupby('month')
            .mean()
            .reset_index(name="national_avg")
        )
        national_trend['date'] = national_trend['month'].dt.to_timestamp()

        state_trend = state_df_trend.groupby('month')['total_enrolments'].sum().reset_index(name='state_total')
        state_trend['date'] = state_trend['month'].dt.to_timestamp()

        trend_df = (
            national_trend[['date', 'national_avg']].merge(state_trend[['date', 'state_total']], on='date', how='outer').sort_values('date').melt(id_vars=['date'], value_vars=['national_avg', 'state_total'], var_name='series', value_name='value')
        )
        trend_df['month_name'] = trend_df['date'].dt.strftime('%b %Y')

        trend_chart = (
            alt.Chart(trend_df)
            .mark_line(point=True)
            .encode(
                x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')),
                y=alt.Y('value:Q', title='Total Enrolments'),
                color=alt.Color('series:N', title='Series'),
                tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('series:N'), alt.Tooltip('value:Q', format=',')]
            )
            .properties(height=320, title='Enrolment Trend: State vs National Average')
        )
        st.altair_chart(alt_dark_chart(trend_chart), use_container_width=True)

        # MoM growth metrics
        monthly_state = state_trend.set_index('date')['state_total'].pct_change()
        monthly_national = national_trend.set_index('date')['national_avg'].pct_change()
        latest_state_growth = monthly_state.dropna().iloc[-1] if len(monthly_state.dropna()) else 0
        latest_national_growth = monthly_national.dropna().iloc[-1] if len(monthly_national.dropna()) else 0

        col4, col5 = st.columns(2)
        col4.metric('Latest State MoM Growth', f"{latest_state_growth:.2%}")
        col5.metric('Latest National MoM growth', f"{latest_national_growth:.2%}")

        if latest_state_growth < latest_national_growth:
            st.warning('State growth is lagging national trend.')
        else:
            st.success('State growth is keeping pace with or exceeding national trend.')

        # District contribution
        st.divider()
        st.subheader('District Contribution within State')
        district_contrib = state_df.groupby('district')['total_enrolments'].sum().reset_index().sort_values('total_enrolments', ascending=False)
        
        district_chart = (
            alt.Chart(district_contrib.head(10))
            .mark_bar(color='#1f4ed8')
            .encode(x=alt.X('total_enrolments:Q', title='Total Enrolments'), y=alt.Y('district:N', sort='-x', title='District'), tooltip=[alt.Tooltip('district:N'), alt.Tooltip('total_enrolments:Q', format=',')])
            .properties(height=360, title='Top 10 Districts by Enrolments')
        )
        st.altair_chart(alt_dark_chart(district_chart), use_container_width=True)

        top3_share = district_contrib.head(3)['total_enrolments'].sum() / state_total * 100 if state_total else 0
        st.metric('Top 3 Districts Contribution', f"{top3_share:.2f}%")

        if top3_share > 50 and len(district_contrib)>5:
            st.warning('Enrolments are highly concentrated in a few districts.')

        # Age-wise distribution
        st.divider()
        st.subheader('Age Group Distribution')
        age_totals = state_df[['age_0_5', 'age_5_17', 'age_18_greater']].sum().reset_index()
        age_totals.columns = ['age_group', 'enrolments']
        age_totals["age_group"] = age_totals["age_group"].replace({
            "age_0_5": "0–5 Years",
            "age_5_17": "5–17 Years",
            "age_18_greater": "18+ Years"
        })
        age_chart = (
            alt.Chart(age_totals)
            .mark_bar(color='#1f4ed8')
            .encode(x=alt.X('age_group:N', title='Age Group', sort=['0–5 Years', '5–17 Years', '18+ Years']), y=alt.Y('enrolments:Q', title='Total Enrolments'), tooltip=[alt.Tooltip('enrolments:Q', format=',')])
            .properties(height=320, title='Enrolments by Age Group')
        )
        st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)

        # Day-of-week distribution
        st.divider()
        st.subheader('Day-of-week Distribution')
        state_df['day_of_week'] = state_df['date'].dt.dayofweek
        age_long = state_df.melt(id_vars=['date', 'day_of_week'], value_vars=['age_0_5', 'age_5_17', 'age_18_greater'], var_name='age_group', value_name='enrolments')
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

def demographic_tab(df_demo, selected_state=None):
    if selected_state:
        st.header(f"{selected_state} — Demographic Update Drilldown")
        state_demo = df_demo[df_demo['state'] == selected_state]

        state_total_updates = int(state_demo['total_updates'].sum())
        total_updates = int(df_demo['total_updates'].sum())

        c1, c2, c3 = st.columns(3)
        c1.metric('Total Demographic Updates', f"{state_total_updates:,}")
        c2.metric('State Share of National Updates', f"{(state_total_updates / total_updates * 100) if total_updates else 0:.2f}%")

        # Trend: state vs national
        state_demo_trend = state_demo.copy()
        state_demo_trend['month'] = state_demo_trend['date'].dt.to_period('M')
        df_demo_trend = df_demo.copy()
        df_demo_trend['month'] = df_demo_trend['date'].dt.to_period('M')
        
        national_trend = (
            df_demo_trend.groupby(['month', 'state'])["total_updates"]
            .sum()
            .groupby('month')
            .mean()
            .reset_index(name="national_avg")
        )
        national_trend['date'] = national_trend['month'].dt.to_timestamp()
        
        state_trend = state_demo_trend.groupby('month')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1).reset_index(name='state_total')
        state_trend['date'] = state_trend['month'].dt.to_timestamp()

        trend_df = (
            national_trend[['date', 'national_avg']].merge(state_trend[['date', 'state_total']], on='date', how='outer').sort_values('date').melt(id_vars=['date'], value_vars=['national_avg', 'state_total'], var_name='series', value_name='value')
        )
        trend_df['month_name'] = trend_df['date'].dt.strftime('%b %Y')

        trend_chart = (
            alt.Chart(trend_df)
            .mark_line(point=True)
            .encode(x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')), y=alt.Y('value:Q', title='Total Demographic Updates'), color=alt.Color('series:N', title='Series'), tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('series:N'), alt.Tooltip('value:Q', format=',')])
            .properties(height=320, title='Demographic Update Trend: State vs National Average')
        )
        st.altair_chart(alt_dark_chart(trend_chart), use_container_width=True)

        monthly_state = state_trend.set_index('date')['state_total'].pct_change()
        monthly_national = national_trend.set_index('date')['national_avg'].pct_change()
        latest_state_growth = monthly_state.dropna().iloc[-1] if len(monthly_state.dropna()) else 0
        latest_national_growth = monthly_national.dropna().iloc[-1] if len(monthly_national.dropna()) else 0
        col4, col5 = st.columns(2)
        col4.metric('Latest State MoM Growth', f"{latest_state_growth:.2%}")
        col5.metric('Latest National MoM growth', f"{latest_national_growth:.2%}")

        if latest_state_growth < latest_national_growth:
            st.warning('State growth is lagging national trend.')
        else:
            st.success('State growth is keeping pace with or exceeding national trend.')

        # District contribution
        st.divider()
        st.subheader('District Contribution within State')
        district_contrib = state_demo.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum().assign(total_updates=lambda x: x.sum(axis=1)).reset_index().sort_values('total_updates', ascending=False)

        district_chart = (
            alt.Chart(district_contrib.head(10))
            .mark_bar(color='#1f4ed8')
            .encode(x=alt.X('total_updates:Q', title='Total Updates'), y=alt.Y('district:N', sort='-x', title='District'), tooltip=[alt.Tooltip('district:N'), alt.Tooltip('total_updates:Q', format=',')])
            .properties(height=360, title='Top 10 Districts by Demographic Updates')
        )
        st.altair_chart(alt_dark_chart(district_chart), use_container_width=True)

        top3_share = district_contrib.head(3)['total_updates'].sum() / state_total_updates * 100 if state_total_updates else 0
        st.metric('Top 3 Districts Contribution', f"{top3_share:.2f}%")
        if top3_share > 50 and len(district_contrib)>5:
            st.warning('Updates are highly concentrated in a few districts.')
        # Age-wise composition
        st.divider()
        st.subheader('Age Group Distribution')
        age_totals = pd.Series({
            'Age 5–17': state_demo['demo_age_5_17'].sum(),
            'Age 17+': state_demo['demo_age_17_'].sum()
        }).reset_index()
        age_totals.columns = ['age_group', 'updates']

        age_chart = (
            alt.Chart(age_totals)
            .mark_bar(color='#1f4ed8')
            .encode(x=alt.X('age_group:N', title='Age Group', sort=['Age 5–17', 'Age 17+']), y=alt.Y('updates:Q', title='Demographic Updates'), tooltip=[alt.Tooltip('updates:Q', format=',')])
            .properties(height=300, title='Demographic Updates by Age Group')
        )
        st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)

        st.divider()
        st.subheader('Day-of-week Distribution')
        state_demo['day_of_week'] = state_demo['date'].dt.dayofweek
        age_long = state_demo.melt(id_vars=['date', 'day_of_week'], value_vars=['demo_age_5_17', 'demo_age_17_'], var_name='age_group', value_name='demographic_updates')
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
        f"Highest demographic update activity observed on "
        f"{['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][peak_day]}."
        )
        st.caption(
            "Day-of-week analysis helps optimize staffing and mobile unit deployment. "
            "Peak activity days may require additional capacity to reduce wait times."
        )

def biometric_tab(df_bio, selected_state=None):
    if selected_state:
        st.header(f"{selected_state} — Biometric Update Drilldown")
        state_bio_df = df_bio[df_bio['state'] == selected_state]

        total_updates = int(state_bio_df[['bio_age_5_17', 'bio_age_17_']].sum().sum())
        national_total = int(df_bio[['bio_age_5_17', 'bio_age_17_']].sum().sum())

        c1, c2, c3 = st.columns(3)
        c1.metric('Total Biometric Updates', f"{total_updates:,}")
        c2.metric('State Share of National Updates', f"{(total_updates / national_total * 100) if national_total else 0:.2f}%")

        # Trend
        state_bio_df_trend = state_bio_df.copy()
        state_bio_df_trend['month'] = state_bio_df_trend['date'].dt.to_period('M')
        df_bio_trend = df_bio.copy()
        df_bio_trend['month'] = df_bio_trend['date'].dt.to_period('M')
        
        national_trend = (
            df_bio_trend.groupby(['month', 'state'])["total_updates"]
            .sum()
            .groupby('month')
            .mean()
            .reset_index(name="national_avg")
        )
        national_trend['date'] = national_trend['month'].dt.to_timestamp()
        
        state_trend = state_bio_df_trend.groupby('month')[['bio_age_5_17', 'bio_age_17_']].sum().sum(axis=1).reset_index(name='state_total')
        state_trend['date'] = state_trend['month'].dt.to_timestamp()

        trend_df = (
            national_trend[['date', 'national_avg']].merge(state_trend[['date', 'state_total']], on='date', how='outer').sort_values('date').melt(id_vars=['date'], value_vars=['national_avg', 'state_total'], var_name='series', value_name='value')
        )
        trend_df['month_name'] = trend_df['date'].dt.strftime('%b %Y')

        trend_chart = (
            alt.Chart(trend_df)
            .mark_line(point=True)
            .encode(x=alt.X('month_name:N', title='Month', sort=alt.EncodingSortField(field='date', order='ascending')), y=alt.Y('value:Q', title='Total Biometric Updates'), color=alt.Color('series:N', title='Series'), tooltip=[alt.Tooltip('month_name:N', title='Month'), alt.Tooltip('series:N'), alt.Tooltip('value:Q', format=',')])
            .properties(height=320, title='Biometric Update Trend: State vs National Average')
        )
        st.altair_chart(alt_dark_chart(trend_chart), use_container_width=True)
        monthly_state = state_trend.set_index('date')['state_total'].pct_change()
        monthly_national = national_trend.set_index('date')['national_avg'].pct_change()
        latest_state_growth = monthly_state.dropna().iloc[-1] if len(monthly_state.dropna()) else 0
        latest_national_growth = monthly_national.dropna().iloc[-1] if len(monthly_national.dropna()) else 0
        col4, col5 = st.columns(2)
        col4.metric('Latest State MoM Growth', f"{latest_state_growth:.2%}")
        col5.metric('Latest National MoM growth', f"{latest_national_growth:.2%}")
        # District contribution
        st.divider()
        st.subheader('District Contribution within State')
        district_updates = state_bio_df.groupby('district')[['bio_age_5_17', 'bio_age_17_']].sum().assign(total_updates=lambda x: x.sum(axis=1)).reset_index().sort_values('total_updates', ascending=False)

        district_chart = (
            alt.Chart(district_updates.head(10))
            .mark_bar(color='#1f4ed8')
            .encode(x=alt.X('total_updates:Q', title='Total Updates'), y=alt.Y('district:N', sort='-x', title='District'), tooltip=[alt.Tooltip('district:N'), alt.Tooltip('total_updates:Q', format=',')])
            .properties(height=360, title='Top 10 Districts by Biometric Updates')
        )
        st.altair_chart(alt_dark_chart(district_chart), use_container_width=True)

        top3_share = district_updates.head(3)['total_updates'].sum() / total_updates * 100 if total_updates else 0
        st.metric('Top 3 Districts Contribution', f"{top3_share:.2f}%")
        if top3_share > 50 and len(district_updates) > 5:
            st.warning('Updates are highly concentrated in a few districts.')
        st.divider()
        st.subheader('Age Group Distribution')
        age_totals = pd.Series({
            'Age 5–17': state_bio_df['bio_age_5_17'].sum(),
            'Age 17+': state_bio_df['bio_age_17_'].sum()
        }).reset_index()
        age_totals.columns = ['age_group', 'updates']

        age_chart = (
            alt.Chart(age_totals)
            .mark_bar(color='#1f4ed8')
            .encode(x=alt.X('age_group:N', title='Age Group', sort=['Age 5–17', 'Age 17+']), y=alt.Y('updates:Q', title='Biometric Updates'), tooltip=[alt.Tooltip('updates:Q', format=',')])
            .properties(height=300, title='Biometric Updates by Age Group')
        )
        st.altair_chart(alt_dark_chart(age_chart), use_container_width=True)

        st.divider()
        st.subheader('Day-of-week Distribution')
        state_bio_df['day_of_week'] = state_bio_df['date'].dt.dayofweek
        age_long = state_bio_df.melt(id_vars=['date', 'day_of_week'], value_vars=['bio_age_5_17', 'bio_age_17_'], var_name='age_group', value_name='biometric_updates')
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
        f"Highest biometric update activity observed on "
        f"{['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][peak_day]}."
        )
        st.caption(
            "Day-of-week analysis helps optimize staffing and mobile unit deployment. "
            "Peak activity days may require additional capacity to reduce wait times."
        )
def main():
    st.title('State Drilldown')
    st.divider()

    try:
        df, df_demo, df_bio = load_aadhaar_data()
    except Exception as e:
        st.error(f'Failed to load data: {e}')
        return
    # Sidebar state selector for state-level drilldowns
    selected_state = st.sidebar.selectbox('Select State ', sorted(df['state'].unique()), index=0)

    tabs = st.tabs(['Enrolment', 'Demographic Updates', 'Biometric Updates'])

    with tabs[0]:
        enrolment_tab(df, selected_state if selected_state != '' else None)

    with tabs[1]:
        demographic_tab(df_demo, selected_state if selected_state != '' else None)

    with tabs[2]:
        biometric_tab(df_bio, selected_state if selected_state != '' else None)


if __name__ == '__main__':
    main()
