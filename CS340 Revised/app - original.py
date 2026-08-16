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

# Configure OS routines
import os

# Configure the plotting routines
import numpy as np
import pandas as pd


# changed animal_shelter and AnimalShelter to match my CRUD Python module file name and class name
from CRUD import AnimalShelter

###########################
# Data Manipulation / Model
###########################
# updated with my username and password and CRUD Python module name

username = "aacuser"
password = "SNHU1234"

# Connect to database via CRUD Module
db = AnimalShelter()

# class read method must support return of list object and accept projection json input
# sending the read method an empty document requests all documents be returned
df = pd.DataFrame.from_records(db.getRecordCriteria({}))

# MongoDB v5+ is going to return the '_id' column and that is going to have an 
# invlaid object type of 'ObjectID' - which will cause the data_table to crash - so we remove
# it in the dataframe here. The df.drop command allows us to drop the column. If we do not set
# inplace=True - it will reeturn a new dataframe that does not contain the dropped column(s)
df.drop(columns=['_id'],inplace=True, errors='ignore')

## Debug
# print(len(df.to_dict(orient='records')))
# print(df.columns)


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

    html.Center(html.A([
    #Placed the HTML image tag 
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
             style={'height':'150px', 'width':'150px'}),], href='https://www.SNHU.edu')),
    #unique identifier
    html.Center(html.B(html.H2('CS-340 Dashboard'))),
    html.Center(html.B(html.H5('Created by Brian Keller'))),
    html.Hr(),
    html.Div(className='row',
         style={'display' : 'flex'},
            children=[
                html.Div(
                #Added radio buttons to select filter
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
    #data table
    dash_table.DataTable(id='datatable-id',
                         columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
                         data=df.to_dict('records'),
    #Changed data table settings
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
#This sets up the dashboard so that your chart and your geolocation chart are side-by-side
    html.Div(className='row',
         style={'display' : 'flex'},
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
    
@app.callback(Output('datatable-id',"data"),
                [Input('checklist', 'value')])
def update_dashboard(filter_type):
## Added code to filter data with MongoDB queries
        df = pd.DataFrame.from_records(db.getRecordCriteria({}))
        
        if filter_type == 'Water Rescue':
            df = pd.DataFrame.from_records(db.read({
                "$and":[
                    {"sex_upon_outcome":"Intact Female"},
                    {"age_upon_outcome_in_weeks":{"$gte":26,"$lte":156}},
                    {"breed":{"$in":["Labrador Retriever Mix",
                                 "Chesapeake Bay Retriever",
                                 "Newfoundland"]}},
                ]
                }))
            
        elif filter_type == 'Disaster Rescue':
            df = pd.DataFrame.from_records(db.getRecordCriteria({
                "$and":[
                    {"sex_upon_outcome":"Intact Male"},
                    {"age_upon_outcome_in_weeks":{"$gte":20,"$lte":300}},
                    {"breed":{"$in":["Doberman Pinscher",
                                     "German Shepherd",
                                     "Golden Retriever",
                                     "Bloodhound",
                                     "Rottweiler"]}},
                ]
                }))
            
        elif filter_type == 'Wilderness Rescue':
            df = pd.DataFrame.from_records(db.getRecordCriteria({
                "$and":[
                    {"sex_upon_outcome":"Intact Male"},
                    {"age_upon_outcome_in_weeks":{"$gte":26,"$lte":156}},
                    {"breed":{"$in":["German Shepherd", 
                                     "Alaskan Malamute", 
                                     "Old English Sheepdog",
                                     "Siberian Husky",
                                     "Rottweiler"]}},
                ]
                }))
            
        df.drop(columns=['_id'],inplace=True, errors='ignore')
        return df.to_dict('records')

    #callback for reset button function
@app.callback(
    Output('checklist', 'value'),
    Input('Reset', 'n_clicks'),
    prevent_initial_call=True
)
def resetSelection(n_clicks):
    return None



# Display the breeds of animal based on quantity represented in
# the data table
@app.callback(Output('graph-id', "children"),[Input('datatable-id', "derived_virtual_data")],prevent_initial_call=True)
def update_graphs(viewData):
    # code to display data to the graph
    dff = pd.DataFrame.from_dict(viewData)
    return [
        dcc.Graph(            
            figure = px.histogram(dff, x='breed', title='Displayed Animals')
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


# This callback will update the geo-location chart for the selected data entry
# derived_virtual_data will be the set of data available from the datatable in the form of 
# a dictionary.
# derived_virtual_selected_rows will be the selected row(s) in the table in the form of
# a list. For this application, we are only permitting single row selection so there is only
# one value in the list.
# The iloc method allows for a row, column notation to pull data from the datatable
@app.callback(Output('map-id', "children"),
        [Input('datatable-id', "derived_virtual_data"),
         Input('datatable-id', "derived_virtual_selected_rows")])
def update_map(viewData, index):  
            if viewData is None:
                return
            elif index is None:
                return

            dff = pd.DataFrame.from_dict(viewData)
        # Because we only allow single row selection, the list can be converted to a row index here
            if index is None:
                row = 0
            else: 
                row = index[0]

        # Austin TX is at [30.75,-97.48]
            return [
            dl.Map(style={'width': '1000px', 'height': '500px'}, center=[30.75,-97.48], zoom=10, children=[
                dl.TileLayer(id="base-layer-id"),
                # Marker with tool tip and popup
                # Column 13 and 14 define the grid-coordinates for the map
                # Column 4 defines the breed for the animal
                # Column 9 defines the name of the animal
                dl.Marker(position=[dff.iloc[row,13],dff.iloc[row,14]], children=[
                    dl.Tooltip(dff.iloc[row,4]),
                    dl.Popup([
                        html.H1("Animal Name"),
                        html.P(dff.iloc[row,9])
                    ])
                ])
            ])
        ]



app.run(debug=True)


