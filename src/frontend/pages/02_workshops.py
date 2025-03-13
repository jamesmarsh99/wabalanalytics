import pandas as pd 
import streamlit as st
from pathlib import Path

# from frontend import graphing_utils


# TODO: Move to graphing utils file

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

## TODO

# TODO: Put in a shared file
WABILI_ICON = str(Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\wabiliIcon.png"))
DATA_CSV = Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\workshops\events.csv")

st.set_page_config(
    page_title="WorkshopAnalytics",
    page_icon=WABILI_ICON,
    layout="wide")

def save_workshops_df_if_valid():
    workshops_df = st.session_state["workshops_df"]
    if workshops_df.name.nunique() < len(workshops_df):
        st.error("Name column must be unique")
        return
    workshops_df.to_csv(DATA_CSV, index=False)
    st.success(f"Saved data")

def add_new_workshop_widget():
    st.button('Add new workshop', on_click=lambda: st.session_state.update({"append_workshop": True}))
    if st.session_state["append_workshop"]:
        with st.form(key='new_workshop_form', clear_on_submit=True):
            st.text_input('Name', key='name')
            st.date_input('Date', key='date')
            st.text_input('workshop_type', key='workshop_type')
            st.selectbox('Collaboration', ['Yes', 'No'], key='collab')
            st.number_input('Attendees', min_value=0, key='attendees')
            st.number_input('Revenue', min_value=0.0, format="%.2f", key='revenue')
            st.number_input('Cost', min_value=0.0, format="%.2f", key='cost')

            def add_workshop():
                new_workshop = {
                    'name': st.session_state['name'],
                    'date': st.session_state['date'],
                    'workshop_type': st.session_state['workshop_type'],
                    'collab': st.session_state['collab'],
                    'attendees': st.session_state['attendees'],
                    'revenue': st.session_state['revenue'],
                    'cost': st.session_state['cost']
                }
                if not new_workshop['name']:
                    st.error("Workshop name cannot be empty")
                    return
                if not new_workshop['workshop_type']:
                    st.error("Workshop type cannot be empty")
                    return
                   
                st.session_state["workshops_df"].loc[st.session_state["workshops_df"].shape[0]] = new_workshop
                # TODO: better place for this casting
                st.session_state["workshops_df"]['date'] = pd.to_datetime(st.session_state["workshops_df"]['date']).dt.date
                st.session_state["append_workshop"] = False
                save_workshops_df_if_valid()
        
            st.form_submit_button("Submit", on_click=add_workshop)
                
    
def add_delete_workshop_widget():
    if st.session_state["append_workshop"]:
        st.stop()
    def delete_workshop():
        st.session_state["workshops_df"] = st.session_state["workshops_df"][st.session_state["workshops_df"]['name'] != st.session_state['workshop_to_delete']]
        save_workshops_df_if_valid()

    with st.form(key='delete_workshop_form'):
        st.selectbox('Delete workshop', options=st.session_state["workshops_df"], key='workshop_to_delete')
        st.form_submit_button("Submit", on_click=delete_workshop)

def aggregate_workshops(workshops_df, cuts):
    AGG_DICT = {
        'date': 'count',
        'attendees': 'mean',
        'revenue': 'mean',
        'cost': 'mean',
        'profit': 'mean',
    }
    if len(cuts) == 0:
        st.error("Please select at least one column to cut the data")
        return
    if len(cuts) > 2 and 'None' in cuts:
        st.error("Only able to select None as the only cut")
    final_agg_dict = {k: v for k, v in AGG_DICT.items() if k not in cuts}
    agg_workshops_df = workshops_df.aggregate(final_agg_dict).T.rename('Aggregated data') \
        if cuts == ['None'] else \
        workshops_df.groupby(cuts).agg(final_agg_dict) 
    RENAME_DICT = {
        'date': 'number of workshops',
        'attendees': 'avg attendees',
        'revenue': 'avg revenue',
        'cost': 'avg cost',
        'profit': 'avg profit'}
    agg_workshops_df = agg_workshops_df.rename(RENAME_DICT)
    return agg_workshops_df


def aggregate_workshops_callback():
    cuts = st.session_state['workshop_cuts']
    st.session_state['agg_workshops_df'] = aggregate_workshops(st.session_state["workshops_df"], cuts)
    

def main():
    # TODO: Maybe dont load the data every time?
    workshops_df = pd.read_csv(DATA_CSV)
    workshops_df['date'] = pd.to_datetime(workshops_df['date']).dt.date

    st.title("Workshop Analytics 🔧")
    st.write("Welcome to Workshop Analytics! See how you've been doing in your workshops!")
    for state_key, default_value in (("workshops_df", workshops_df),
                                    ("agg_workshops_df", None),
                                    ("edit_mode", False),
                                    ("append_workshop", False),
                                    ("save_workshops", False)):
        if state_key not in st.session_state:
            st.session_state[state_key] = default_value

    st.toggle('Edit mode',
              value=st.session_state["edit_mode"],
              help='Toggle to edit your workshop data! Make sure you have unique names.',
              on_change=lambda: st.session_state.update({"edit_mode": not st.session_state["edit_mode"]}))

    st.session_state["workshops_df"] = st.session_state["workshops_df"].sort_values(by='date').reset_index(drop=True)
    if st.session_state["edit_mode"]:
        edited_df = st.data_editor(st.session_state["workshops_df"], use_container_width=True)
        if edited_df is not None and not edited_df.equals(st.session_state["workshops_df"]):
            st.session_state["workshops_df"] = edited_df
            save_workshops_df_if_valid()
        add_new_workshop_widget()
        add_delete_workshop_widget()
        st.stop()
        
    st.session_state["workshops_df"]['profit'] = st.session_state["workshops_df"]['revenue'] - st.session_state["workshops_df"]['cost']
    workshops_df = st.session_state["workshops_df"]
    with st.form(key='Compute workshops data'):
        available_cuts = list(col for col in st.session_state["workshops_df"].columns if st.session_state["workshops_df"][col].dtype in ('object', 'str')) + ['None']
        st.multiselect("Cut",
                       available_cuts,
                       default=['None'],
                       max_selections=2,
                       help="Choose how you want to cut + slice the data. Choosing None will aggregate all your data together",
                       key='workshop_cuts')
        st.form_submit_button("Submit", on_click=aggregate_workshops_callback)

    agg_workshops_df = st.session_state["agg_workshops_df"]
    if agg_workshops_df is None:
        st.stop()
        
    st.dataframe(agg_workshops_df)

    timeseries_col = st.selectbox("See timeseries",
                                  [None] + [col for col in st.session_state["workshops_df"].columns if st.session_state["workshops_df"][col].dtype in ('int64', 'float64')])
    if timeseries_col is not None:
        cuts = list(agg_workshops_df.index.names)
        if cuts == [None]:
            cuts = []
        timeseries_df = aggregate_workshops(st.session_state["workshops_df"], cuts + ['date'])        
        plot_line_chart(timeseries_df.reset_index(), 'date', timeseries_col, plotting_axes=cuts, title=f"{timeseries_col} over time")

main()