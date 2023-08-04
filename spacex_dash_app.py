# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
launch_sites = spacex_df["Launch Site"].unique()
dropDownOptions = [{"label": "All Sites", "value": "All"}]
dropDownOptions.extend(
    {"label": launch_site, "value": launch_site} for launch_site in launch_sites
)
min_payload, max_payload = (
    spacex_df["Payload Mass (kg)"].min(),
    spacex_df["Payload Mass (kg)"].max(),
)
print(min_payload, max_payload)
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        # Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id="site-dropdown",
            options=dropDownOptions,
            value="All",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),
        html.Br(),
        # Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        # Add a slider to select payload range
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={0: "0", 2500: "2500", 5000: "5000", 7500: "7500", 10000: "10000"},
            value=[min_payload, max_payload],
        ),
        # Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "All":
        filtered_df = (
            spacex_df[spacex_df["class"] == 1].groupby("Launch Site").count()["class"]
        )
        fig = px.pie(
            filtered_df,
            values=filtered_df.values,
            names=filtered_df.index,
            title="Total Success Lanuches By Site",
        )
        return fig
    else:
        filtered_df = pd.DataFrame(
            spacex_df[spacex_df["Launch Site"] == entered_site].groupby("class").count()
        )["Launch Site"]
        fig = px.pie(
            filtered_df,
            values=filtered_df.values,
            names=filtered_df.index,
            title="Total Lanuches for site " + entered_site,
        )
        return fig
        # return the outcomes piechart for a selected site


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(launch_site: str, payload_range: float):
    filtered_data = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= payload_range[0])
        & (spacex_df["Payload Mass (kg)"] <= payload_range[1])
    ]
    if launch_site == "All":
        fig = px.scatter(
            filtered_data,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
        )
    else:
        fig = px.scatter(
            filtered_data[(spacex_df["Launch Site"] == launch_site)],
            y="class",
            color="Booster Version Category",
        )
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server()
