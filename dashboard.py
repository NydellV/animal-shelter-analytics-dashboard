from dash import Dash, dcc, html, dash_table, Input, Output
import plotly.express as px
import pandas as pd
from crud import AnimalShelter
from bson import ObjectId


def convert_objectid(obj):
    if isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj


# Connect to local MongoDB (no credentials needed for local dev)
shelter = AnimalShelter(host='localhost', port=27017)

initial_data = shelter.read({"Animal Type": {"$exists": True}})
initial_data = convert_objectid(initial_data)
df = pd.DataFrame(initial_data)

# Rescue type filter mapped to Breed values in the Austin dataset
rescue_type_mapping = {
    "Water Rescue": ["Labrador Retriever Mix"],
    "Mountain or Wilderness Rescue": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", "Siberian Husky", "Rottweiler"],
    "Disaster or Individual Tracking": ["Doberman Pinscher", "German Shepherd", "Golden Retriever", "Bloodhound", "Rottweiler"]
}

app = Dash(__name__)
app.title = "Grazioso Salvare Dashboard"

app.layout = html.Div([
    html.H2("Grazioso Salvare Animal Outcomes Dashboard", style={"textAlign": "center"}),
    html.P("By Nydell Vera", style={"textAlign": "center", "fontStyle": "italic"}),

    html.Div([
        html.Label("Select Rescue Type:"),
        dcc.RadioItems(
            id="rescue-type",
            options=[
                {"label": "All", "value": "All"},
                {"label": "Water Rescue", "value": "Water Rescue"},
                {"label": "Mountain or Wilderness Rescue", "value": "Mountain or Wilderness Rescue"},
                {"label": "Disaster or Individual Tracking", "value": "Disaster or Individual Tracking"}
            ],
            value="All",
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        )
    ], style={"padding": "20px"}),

    dash_table.DataTable(
        id="datatable",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        page_size=10,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "minWidth": "100px", "maxWidth": "180px", "whiteSpace": "normal"}
    ),

    html.Br(),
    dcc.Graph(id="breed-chart")
])


@app.callback(
    [Output("datatable", "data"),
     Output("breed-chart", "figure")],
    [Input("rescue-type", "value")]
)
def update_dashboard(selected_rescue):
    if selected_rescue == "All":
        query = {"Animal Type": {"$exists": True}}
    else:
        query = {"Breed": {"$in": rescue_type_mapping[selected_rescue]}}

    data = shelter.read(query)
    data = convert_objectid(data)
    df_filtered = pd.DataFrame(data)

    if df_filtered.empty:
        df_filtered = pd.DataFrame(columns=df.columns)

    # Breed bar chart
    if "Breed" in df_filtered.columns:
        breed_counts = df_filtered["Breed"].value_counts().nlargest(10).reset_index()
        breed_counts.columns = ["Breed", "Count"]
        breed_fig = px.bar(breed_counts, x="Breed", y="Count", title="Top 10 Breeds")
    else:
        breed_fig = px.bar(title="No Breed Data Available")

    return df_filtered.to_dict("records"), breed_fig


if __name__ == "__main__":
    app.run(debug=True, port=8051)
