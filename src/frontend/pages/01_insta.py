import pandas as pd 
import streamlit as st
from pathlib import Path
from enum import Enum
import datetime as dt
import altair as alt
# import matplotlib.dates as mpl_dates

# TODO: Move to graphing utils file

import plotly.express as px
import streamlit as st
from typing import List

PLOTLY_CONFIG_OPTIONS = {
    'displayLogo': False,
    'modeBarButtonsToAdd': ['hoverclosest', 'hovercompare', 'toggleSpikelines'],
}

COLORS = ['green', 'blue', 'red', 'purple', 'orange', 'yellow', 'pink', 'brown', 'black', 'gray']

def line_chart(df: pd.DataFrame, x_axis_col: str, y_axis_col: str, plotting_axes: List[str] | None = None,
               title: str | None = None):
    if plotting_axes is None:
        plotting_axes = []
    if x_axis_col not in df.columns or y_axis_col not in df.columns:
        raise ValueError(f"Columns {x_axis_col} and {y_axis_col} must be in the DataFrame")
    if len(plotting_axes) > 2:
        raise ValueError("You can only have 2 plotting axes")
    
    color_axis, dash_axis = plotting_axes + [None] * (2 - len(plotting_axes))
    return px.line(df,
                   x=x_axis_col,
                   y=y_axis_col,
                   color=color_axis,
                   line_dash=dash_axis,
                   title=title)

## TODO

# TODO: Put in a shared file
WABILI_ICON = str(Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\wabiliIcon.png"))

st.set_page_config(
    page_title="InstaAnalytics",
    page_icon=WABILI_ICON,
    layout="wide")

class InstagramAnalyticsType(Enum):
    FOLLOWERS = 'Followers'
    POSTS = 'Posts'

def get_followers_data() -> pd.DataFrame:
    # Load the data
    INSTA_DATA_DIR = Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\instagram\profile")
    files = [file for file in INSTA_DATA_DIR.iterdir() ]
    df = pd.concat([pd.read_csv(file) for file in files])
    df['date'] = pd.to_datetime(df['date'])
    WORKSHOPS_DATA_CSV = Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\workshops\events.csv")
    workshops_df = pd.read_csv(WORKSHOPS_DATA_CSV)
    workshops_df['profit'] = workshops_df['revenue'] - workshops_df['cost']
    
    return df, workshops_df

def get_posts_data() -> pd.DataFrame:
    # Load the data
    INSTA_DATA_DIR = Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\instagram\posts")
    # get the latest file, which will be the max value
    df = pd.read_csv(max(INSTA_DATA_DIR.iterdir()))
    df['date'] = pd.to_datetime(df['time'])
    return df

st.title("Instagram Analytics 📸")
st.write("Welcome to Instagram Analytics! This page updates automatically every hour. Enjoy!")

analytics_type = InstagramAnalyticsType(st.pills('Analytics type', ['Posts', 'Followers'], default='Posts'))

if analytics_type == InstagramAnalyticsType.FOLLOWERS:
    followers_df, workshops_df = get_followers_data()
    chart = line_chart(followers_df, 'date', 'followers', plotting_axes=[], title=f"@wabiliworkshop followers over time")
    show_events = st.toggle('Show significant events', value=True)
    if show_events:
        workshop_event_types = list(workshops_df['workshop_type'].unique())
        for i, row in workshops_df.iterrows():
            x_vline = (pd.Timestamp(row['date']) - pd.Timestamp('1970-01-01')) // pd.Timedelta('1ms')
            hovertext = f'Revenue: ${row["revenue"]:.2f}<br>Cost: ${row["cost"]:.2f}<br>Profit: ${row["profit"]:.2f}'
            text = row['name'].replace(' ', '<br>')
            color = COLORS[workshop_event_types.index(row['workshop_type']) % len(COLORS)]
            chart.add_vline(x=x_vline, line_width=3, line_dash="dash", line_color=color,
                            annotation=dict(x=x_vline, 
                                            text=text,
                                            hovertext=hovertext, 
                                            font_family="Helvetica",
                                            yanchor="bottom",
                                            xshift=-30,
                                            hoverlabel=dict(bgcolor="grey",
                                                            font_family="Helvetica")))
    st.plotly_chart(chart, config=PLOTLY_CONFIG_OPTIONS)

if analytics_type == InstagramAnalyticsType.POSTS:
    df = get_posts_data()
    metric = st.pills('Metric', ['like_count', 'comment_count'], default='like_count')

    st.altair_chart(alt.Chart(df).mark_circle().encode(
        x='date',
        y=alt.Y(metric, scale=alt.Scale(domain=[0, 1.1 * df[metric].max()])),
        color=metric,
        size=alt.Size(metric, scale=alt.Scale(range=[400, 800])),
        tooltip=['date', 'caption', 'like_count', 'comment_count']
    ).interactive())
