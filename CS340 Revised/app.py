# Setup the Jupyter version of Dash
from dash import Dash

# Configure the necessary Python module imports for dashboard components
import dash_leaflet as dl
from dash import dcc
from dash import html
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output, State
import base64
import os
import numpy as np
import pandas as pd
import json
import time
from CRUD import AnimalShelter

username = "aacuser"
password = "SNHU1234"


db = AnimalShelter()
db.createIndexes()
df = pd.DataFrame.from_records(db.getRecordCriteria({}))
df.drop(columns=['_id'],inplace=True, errors='ignore')

#########################
# Dashboard Layout / View
#########################
app = Dash(__name__)

#Added in Grazioso Salvare’s logo
image_filename = 'Grazioso Salvare Logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#style for button
buttonStyle = {'background-color': 'white',
                      'color': 'black',
                      'height': '30px',
                      'width': '100px',
                      'margin-left': '40px'}

app.layout = html.Div([
    html.Div([
        html.A(
            html.Img(
                src="data:image/png;base64,{}".format(encoded_image.decode()),
                style={
                    "height": "80px",
                    "width": "80px"
                }
            ),
            href="https://www.SNHU.edu",
            style={"justifySelf": "start"}
        ),
        html.Div([
            html.H2(
                "CS-499 Dashboard Revision",
                style={"margin": "0"}
            ),
            html.H5(
                "Created by Brian Keller",
                style={"margin": "8px 0 0 0"}
            )
        ], style={"textAlign": "center"}),

        html.Div()
    ], style={
        "display": "grid",
        "gridTemplateColumns": "150px 1fr 150px",
        "alignItems": "center",
        "padding": "10px 25px"
    }),
    html.Hr(),
    html.Div(className='row',
         style={'display' : 'flex'},
            children=[
                html.Div(

                dcc.RadioItems(id='checklist',
                options=['Water Rescue', 'Wilderness Rescue', 'Disaster Rescue'],
                inline=True),
                ),
                # Added reset button
                html.Div(className='buttons',
                style={'display':'flex'},
                children=[
                    html.Button(id='Reset', n_clicks=0, children='Reset', style = buttonStyle)
                ]),
            ]),
    html.Div([

        html.Div([
            html.Label("Animal Type"),
            dcc.Dropdown(
                id="animal-type-filter",
                options=[
                    {"label": animal_type, "value": animal_type}
                    for animal_type in sorted(
                        df["animal_type"].dropna().unique()
                    )
                ],
                multi=True,
                placeholder="Select animal types"
            )
        ], style={"minWidth": "220px", "flex": "1"}),

        html.Div([
            html.Label("Breed"),
            dcc.Dropdown(
                id="breed-filter",
                options=[
                    {"label": breed, "value": breed}
                    for breed in sorted(df["breed"].dropna().unique())
                ],
                multi=True,
                placeholder="Select breeds"
            )
        ], style={"minWidth": "300px", "flex": "2"}),

        html.Div([
            html.Label("Sex"),
            dcc.Dropdown(
                id="sex-filter",
                options=[
                    {"label": sex, "value": sex}
                    for sex in sorted(
                        df["sex_upon_outcome"].dropna().unique()
                    )
                ],
                multi=True,
                placeholder="Select sex"
            )
        ], style={"minWidth": "220px", "flex": "1"}),

        html.Div([
            html.Label("Outcome Type"),
            dcc.Dropdown(
                id="outcome-type-filter",
                options=[
                    {"label": outcome, "value": outcome}
                    for outcome in sorted(
                        df["outcome_type"].dropna().unique()
                    )
                ],
                multi=True,
                placeholder="Select outcome types"
            )
        ], style={"minWidth": "220px", "flex": "1"}),

        html.Div([
            html.Label("Age in Weeks"),
            html.Div([
                dcc.Input(
                    id="minimum-age-filter",
                    type="number",
                    min=0,
                    placeholder="Minimum",
                    style={"width": "140px"}
                ),
                dcc.Input(
                    id="maximum-age-filter",
                    type="number",
                    min=0,
                    placeholder="Maximum",
                    style={"width": "140px"}
                )
            ], style={
                "display": "flex",
                "gap": "10px"
            })
        ], style={"minWidth": "300px", "flex": "1"})

    ], style={
        "display": "flex",
        "gap": "15px",
        "alignItems": "flex-end",
        "flexWrap": "wrap",
        "margin": "15px 0"
    }),
    html.Div(
        id="cache-status",
        style={
            "margin": "10px 0",
            "fontWeight": "bold"
        }
    ),
    html.Div(
        id="statistics-summary",
        style={
            "display": "flex",
            "gap": "15px",
            "margin": "15px 0",
            "flexWrap": "wrap"
        }
    ),
    dash_table.DataTable(id='datatable-id',
                         columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
                         data=df.to_dict('records'),
        editable = False,
        sort_action = "native",
        sort_mode = "multi",
        page_action = "native",
        page_current = 0, 
        page_size = 15,
        row_selectable = "single",
        selected_rows = [0],
        style_cell={'textAlign': 'left'},
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(220, 220, 220)',
        }
        ],
        style_header={
        'backgroundColor': 'rgb(108, 152, 118)',
        'color': 'Black',
        'fontWeight': 'bold'
        }
        
    ),
    html.Br(),
    html.Br(),
    html.Hr(),
    html.Div(className='row',
             style={
                 'display': 'flex',
                 'gap': '20px',
                 'alignItems': 'flex-start',
                 'flexWrap': 'wrap',
                 'marginTop': '20px'
             },
             children=[
        html.Div(
            id='graph-id',
            className='col s12 m6',
            ),
        html.Div(
            id='map-id',
            className='col s12 m6',
            )
        ])
])
#############################################
# Interaction Between Components / Controller
#############################################
def build_query(
    animal_types=None,
    breeds=None,
    sexes=None,
    outcome_types=None,
    minimum_age=None,
    maximum_age=None
):
    query = {}
    if animal_types:
        query["animal_type"] = {"$in": animal_types}
    if breeds:
        query["breed"] = {"$in": breeds}
    if sexes:
        query["sex_upon_outcome"] = {"$in": sexes}
    if outcome_types:
        query["outcome_type"] = {"$in": outcome_types}
    age_query = {}
    if minimum_age is not None:
        age_query["$gte"] = minimum_age
    if maximum_age is not None:
        age_query["$lte"] = maximum_age
    if age_query:
        query["age_upon_outcome_in_weeks"] = age_query
    return query

query_cache = {}

def get_cached_records(query):
    """Return cached results or query MongoDB when needed."""

    cache_key = json.dumps(query, sort_keys=True)
    start_time = time.perf_counter()

    if cache_key in query_cache:
        records = query_cache[cache_key]
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        print(f"Using cached results: {elapsed_ms:.3f} ms")

        return (
            records,
            f"Cached results loaded in {elapsed_ms:.3f} ms"
        )

    records = list(db.getRecordCriteria(query))
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    query_cache[cache_key] = records

    print(f"MongoDB query completed: {elapsed_ms:.3f} ms")

    return (
        records,
        f"Fresh MongoDB results loaded in {elapsed_ms:.3f} ms"
    )
@app.callback(
    Output("datatable-id", "data"),
    Output("cache-status", "children"),
    Input("checklist", "value"),
    Input("animal-type-filter", "value"),
    Input("breed-filter", "value"),
    Input("sex-filter", "value"),
    Input("outcome-type-filter", "value"),
    Input("minimum-age-filter", "value"),
    Input("maximum-age-filter", "value")
)
def update_dashboard(filter_type,
                     animal_types,
                     breeds,
                     sexes,
                     outcome_types,
                     minimum_age,
                     maximum_age):
    query = build_query(
        animal_types=animal_types,
        breeds=breeds,
        sexes=sexes,
        outcome_types=outcome_types,
        minimum_age=minimum_age,
        maximum_age=maximum_age
    )
    if filter_type == "Water Rescue":
        query = build_query(
            animal_types=animal_types,
            outcome_types=outcome_types,
            sexes=["Intact Female"],
            breeds=[
                "Labrador Retriever Mix",
                "Chesapeake Bay Retriever",
                "Newfoundland"
            ],
            minimum_age=26,
            maximum_age=156
        )
    elif filter_type == "Wilderness Rescue":
        query = build_query(
            animal_types=animal_types,
            outcome_types=outcome_types,
            sexes=["Intact Male"],
            breeds=[
                "German Shepherd",
                "Alaskan Malamute",
                "Old English Sheepdog",
                "Siberian Husky",
                "Rottweiler"
            ],
            minimum_age=26,
            maximum_age=156
        )
    elif filter_type == "Disaster Rescue":
        query = build_query(
            animal_types=animal_types,
            outcome_types=outcome_types,
            sexes=["Intact Male"],
            breeds=[
                "Doberman Pinscher",
                "German Shepherd",
                "Golden Retriever",
                "Bloodhound",
                "Rottweiler"
            ],
            minimum_age=20,
            maximum_age=300
        )
    records, cache_status = get_cached_records(query)
    df = pd.DataFrame.from_records(records)
            
    df.drop(columns=['_id'],inplace=True, errors='ignore')
    return df.to_dict('records'), cache_status

@app.callback(
    Output("statistics-summary", "children"),
    Input("datatable-id", "data")
)
def update_statistics(table_data):

    if not table_data:
        return html.P("No statistics available for the selected filters.")

    filtered_df = pd.DataFrame.from_records(table_data)

    total_animals = len(filtered_df)

    ages = pd.to_numeric(
        filtered_df.get("age_upon_outcome_in_weeks"),
        errors="coerce"
    )

    average_age = ages.mean()

    most_common_breed = (
        filtered_df["breed"].mode().iloc[0]
        if "breed" in filtered_df and not filtered_df["breed"].dropna().empty
        else "N/A"
    )

    most_common_outcome = (
        filtered_df["outcome_type"].mode().iloc[0]
        if "outcome_type" in filtered_df
        and not filtered_df["outcome_type"].dropna().empty
        else "N/A"
    )

    card_style = {
        "padding": "15px",
        "border": "1px solid #cccccc",
        "borderRadius": "6px",
        "minWidth": "180px",
        "backgroundColor": "#f7f7f7"
    }

    return [
        html.Div([
            html.H4("Matching Animals"),
            html.P(f"{total_animals:,}")
        ], style=card_style),

        html.Div([
            html.H4("Average Age"),
            html.P(
                f"{average_age:.1f} weeks"
                if pd.notna(average_age)
                else "N/A"
            )
        ], style=card_style),

        html.Div([
            html.H4("Most Common Breed"),
            html.P(most_common_breed)
        ], style=card_style),

        html.Div([
            html.H4("Most Common Outcome"),
            html.P(most_common_outcome)
        ], style=card_style)
    ]

@app.callback(
    Output("checklist", "value"),
    Output("animal-type-filter", "value"),
    Output("breed-filter", "value"),
    Output("sex-filter", "value"),
    Output("outcome-type-filter", "value"),
    Output("minimum-age-filter", "value"),
    Output("maximum-age-filter", "value"),
    Input("Reset", "n_clicks"),
    prevent_initial_call=True
)
def reset_selection(n_clicks):
    return None, [], [], [], [], None, None

@app.callback(
    Output("graph-id", "children"),
    Input("datatable-id", "derived_virtual_data")
)
def update_graphs(viewData):

    if not viewData:
        return html.P("No animals match.")

    dff = pd.DataFrame.from_records(viewData)

    if "breed" not in dff.columns:
        return html.P("No breed data is available.")

    return [
        dcc.Graph(
            figure=px.histogram(
                dff,
                x="breed",
                title="Displayed Animals"
            )
        )
    ]
    
#This callback will highlight a cell on the data table when the user selects it
@app.callback(
        Output('datatable-id', 'style_data_conditional'),
        [Input('datatable-id', 'selected_columns')],
    )
def update_styles(selected_columns):
    if selected_columns == None:
        return
    else:
        return [{
            'if': { 'column_id': i },
            'background_color': '#D2F3FF'
        } for i in selected_columns]

@app.callback(
    Output("map-id", "children"),
    Input("datatable-id", "data"),
    Input("datatable-id", "selected_rows")
)
def update_map(viewData, selected_rows):

    if not viewData:
        return html.P("No location available.")

    dff = pd.DataFrame.from_records(viewData)

    required_columns = {
        "location_lat",
        "location_long",
        "breed",
        "name"
    }

    if not required_columns.issubset(dff.columns):
        return html.P("Location data is unavailable.")

    if selected_rows and selected_rows[0] < len(dff):
        row = selected_rows[0]
    else:
        row = 0

    animal = dff.iloc[row]

    latitude = animal["location_lat"]
    longitude = animal["location_long"]

    if pd.isna(latitude) or pd.isna(longitude):
        return html.P("This animal does not have valid location data.")

    return [
        dl.Map(
            style={"width": "700px", "height": "500px"},
            center=[latitude, longitude],
            zoom=10,
            children=[
                dl.TileLayer(),

                dl.Marker(
                    position=[latitude, longitude],
                    children=[
                        dl.Tooltip(str(animal["breed"])),

                        dl.Popup([
                            html.H4("Animal Name"),
                            html.P(str(animal["name"]))
                        ])
                    ]
                )
            ]
        )
    ]
app.run(debug=True)


