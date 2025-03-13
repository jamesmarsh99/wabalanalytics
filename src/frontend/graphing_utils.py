import plotly
import plotly.express as px
import streamlit as st
from typing import List
import pandas as pd

PLOTLY_CONFIG_OPTIONS = {
    'displayLogo': False,
    'modeBarButtonsToAdd': ['hoverclosest', 'hovercompare', 'toggleSpikelines'],
}

def plot_line_chart(df: pd.DataFrame, x_axis_col: str, y_axis_col: str, plotting_axes: List[str] | None = None,
               title: str | None = None):
    if plotting_axes is None:
        plotting_axes = []
    if x_axis_col not in df.columns or y_axis_col not in df.columns:
        raise ValueError(f"Columns {x_axis_col} and {y_axis_col} must be in the DataFrame")
    if len(plotting_axes) > 2:
        raise ValueError("You can only have 2 plotting axes")
    
    color_axis, dash_axis = plotting_axes + [None] * (2 - len(plotting_axes))
    chart = px.line(df,
                   x=x_axis_col,
                   y=y_axis_col,
                   color=color_axis,
                   line_dash=dash_axis,
                   title=title)
    st.plotly_chart(chart, config=PLOTLY_CONFIG_OPTIONS)