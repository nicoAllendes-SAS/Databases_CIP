#All librarys: #
import dash
from dash import dcc, html,dash_table, State
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gdp
import numpy as np

###########################

# Load datafiles: ############
# Load the diabetes data from the provided CSV link
diabetes_data_url = "https://github.com/plotly/datasets/raw/master/diabetes-vid.csv"
diabetes_df = pd.read_csv(diabetes_data_url)

# Load the gapminder data for DataTable and histogram
gapminder_data_url = "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
gapminder_df = pd.read_csv(gapminder_data_url)

# Mapbox access token (replace with your own token)
mapbox_access_token = "pk.eyJ1Ijoibmljb2xhcy1hbGxlbmRlcy1nemUiLCJhIjoiY2xwaW9qcndiMDE1azJxdGo5bDF4anNrYyJ9.Sxhjp0Tm8KOJQ4MDgJZo7g"

#LEE LOS geoJSON recien creados:

#500 kV: ################################
geojson_df_500_kv = gdp.read_file('MEN_electric_lines/subset_df_500kv_ministerio.geojson')
geojson_df_500_kv['LONG_KM'] = np.round(geojson_df_500_kv['LONG_KM'],decimals = 2)

#345 kV: ################################
geojson_df_220_kv = gdp.read_file('MEN_electric_lines/subset_df_345kv_ministerio.geojson')
geojson_df_220_kv['LONG_KM'] = np.round(geojson_df_220_kv['LONG_KM'],decimals = 2)

# Lee las subestaciones (S/E) en formato geojson:
#Lee el geojson:
df_subestaciones_ministerio_geojson = gdp.read_file('zipfolder_subestaciones_geojson/subestaciones_ministerio.geojson')

#############


####### ajusta la data de las líneas de 500 kv en formato geojson:
#Incorpora las línas de transmisión a 500 kV:

#Array auxiliares donde se almacenan las coordenadas (lat,long) de los linestring + nombre de las líneas (names):
lats = []
lons = []
names = []

#indice utilizado para cambiar los valores nombre_linea_transmision dentro del array auxiliar names
pos_inicial = 0 

#recorre los linestring del df 500 kv:
for linestring in geojson_df_500_kv['geometry']:
       
       #para cada conjunto de linestring almacena las coordenadas lat, long en formato lista lat = [34,45,54], long = [34,54,54] 
       #donde lat = y, long = x
       x, y = linestring.xy


       #agrega al array auxiliar la lista con las coordenadas asociadas a latitud (y) del linestring[i]
       lats = np.append(lats, y)

       #agrega al array auxiliar la lista con las coordenadas asociadas a longitud (x) del linestring[i]
       lons = np.append(lons, x)
       
       #print("repetir nombre",geojson_df_500_kv['NOMBRE'][pos_inicial],len(y),"veces")

       #Recorre el largo del linestring[i] y repite len(y) veces el nombre de la líneas de transmisión en el array names
       #con esto consigue que al realizar hover_linestring salga el nombre de la linea durante todo el linestring
       for i in range(len(y)+1):
              names.append(geojson_df_500_kv['NOMBRE'][pos_inicial])
       

       #una vez recorrido todos los elementos del linestring[i], pasa a la siguiente posición (linestring[i+1])
       pos_inicial = pos_inicial +1

       #agrega un none al final del array auxiliar que almacena las coordenadas lats, lons, para evitar que al unir los linestring se generen 
       #conexiones inexistentes. 
       lats = np.append(lats, None)
       lons = np.append(lons, None)


################## end ajuste geojson 500 kv #########

# ajuste líneas de 345 kv: #######################
geojson_df_220_kv.head()
lats_220 = []
lons_220 = []
names_220 = []
pos_inicial = 0

for linestring in geojson_df_220_kv['geometry']:
       #print(linestring)
       
       x, y = linestring.xy

       lats_220 = np.append(lats_220, y)
       lons_220 = np.append(lons_220, x)
       
       for i in range(len(y)+1):
              
              names_220.append(geojson_df_220_kv['NOMBRE'][pos_inicial])
             
       #una vez recorrido todos los elementos del linestring[i], pasa a la siguiente posición (linestring[i+1])
       pos_inicial = pos_inicial +1
      
       #agrega el espacio none
       lats_220 = np.append(lats_220, None)
       lons_220 = np.append(lons_220, None)
       

########## end ajuste líneas 345 kv: ##############


###################### Mapa inicial : ###################################3
#Crea mapa: #######################
       
#Mapa con las subestaciones del SEN: 
fig = px.scatter_mapbox(
        df_subestaciones_ministerio_geojson, 
        lat=df_subestaciones_ministerio_geojson['geometry'].y,
        lon=df_subestaciones_ministerio_geojson['geometry'].x,
        hover_name="NOMBRE",
        hover_data=["PROPIEDAD","TENSION_KV"],
        color_discrete_sequence=["black"],
        zoom=3,
        width= 20,
        height=500
        )

# end mapa: ######################################


############# descomentar ##############################
#Agrega las subestaciones a la leyenda:
for trace in fig.data:
    trace.showlegend = True
    trace.name = 'Substations (S/E)'  # Asigna un nombre para la leyenda del scatter plot

#Crea las líneas de 500 kv:
# Add lines for 500 kv transmission
fig2 = px.line_mapbox(geojson_df_500_kv, 
                      lat=lats, 
                      lon=lons, 
                      hover_name=names, 
                      zoom=3, 
                      height=500)

#Incorpora las Lineas de 500 kv al mapa junto con su leyenda:
# Line trace for 500 kv
line_500_kv = fig2.data[0]
line_500_kv.showlegend = True
line_500_kv.name = 'Transmission Lines: 500 kV line'
line_500_kv.marker.color = 'red'  # Set line color to red
fig.add_trace(line_500_kv)

#Crea las líneas de 345 kv:
# Add lines for 345 kv transmission
fig3 = px.line_mapbox(geojson_df_220_kv, 
                      lat=lats_220, 
                      lon=lons_220, 
                      hover_name=names_220,  
                      zoom=3, 
                      height=500)

#Incorpora las Lineas de 345 kv al mapa junto con su leyenda:
# Line trace for 345 kv
line_345_kv = fig3.data[0]
line_345_kv.showlegend = True
line_345_kv.name = 'Transmission Lines: 345 kV line'
line_345_kv.marker.color = 'yellow'  # Set line color to yellow
fig.add_trace(line_345_kv)

# actualiza el color de la línea de 500 kv a rojo.
fig.update_traces(line=dict(color='red'), selector=1)
#actualiza el color de la linea de 345 kv a amarillo.
fig.update_traces(line=dict(color='yellow'), selector=2)

#Agrega la leyenda al mapa y la capa (en este caso la capa de open-street-map): 
fig.update_layout(
    showlegend=True,
    legend_title_text='Legend',  # Título de la leyenda
    legend=dict(
        yanchor="bottom",
        y=0.01,
        xanchor="left",
        x=0.01,
        bgcolor='rgba(255,255,255,0.5)'  # Fondo semi-transparente para la leyenda
    ),
    mapbox_style="white-bg",
    mapbox_layers=[{
        "below": 'traces',
        "sourcetype": "raster",
        "sourceattribution": "Powered by Grid and Zero energy consulting",
        "source": [
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        ]
    }],
    margin={"r":0,"t":0,"l":0,"b":0}
)

#Agrega la imagen del logo de la empresa (Grid and zero energy consulting)
fig.add_layout_image(
    dict( #"https://i.imgur.com/Dvbcc0N.jpeg"
        source="https://i.imgur.com/Dvbcc0N.jpeg",  # Sustituye con la ruta a tu imagen
        xref="paper", yref="paper",
        x=0.99, y=0.1,
        sizex=0.25, sizey=0.25,  # Tamaño de la imagen en proporción al tamaño del gráfico
        xanchor="right", yanchor="bottom"
    )
)

############# descomentar ##############################

############ end nuevo:

# #Add lineas de transmisión de 500 kv:
# fig2 = px.line_mapbox(geojson_df_500_kv, lat=lats, lon= lons, hover_name= names, zoom=3, height=20)
# fig.add_trace(fig2.data[0])

# #Add lineas de transmisión de 345 kv:
# fig3 = px.line_mapbox(geojson_df_220_kv, lat=lats_220, lon= lons_220, hover_name=names_220,  zoom=3, height=20)
# fig.add_trace(fig3.data[0])


# # actualiza el color de la línea de 500 kv a rojo.
# fig.update_traces(line=dict(color='red'), selector=1)
# #actualiza el color de la linea de 345 kv a amarillo.
# fig.update_traces(line=dict(color='yellow'), selector=2)


# fig.update_layout(
#     mapbox_style="white-bg",
#     #mapbox_style='open-street-map',
#     mapbox_layers=[
#         {
#             "below": 'traces',
#             "sourcetype": "raster",
#             "sourceattribution": "Powered by Grid and Zero energy consulting",
#             "source": [
#                 "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
#             #     #"https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
#             ]
#         }
        
#       ])
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



# Create the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = html.Div([
    # Black banner with CIP image and title
    html.Div([
        html.Img(src="https://www.un.org/sites/un2.un.org/files/2021/09/cip.png", style={'width': '100px'}),
        html.H1("Dashboard for CIP", style={'color': 'white'}),
        html.P("This dashboard provides insights into  global data.", style={'color': 'white'}),
    ], style={'background-color': 'black', 'padding': '20px'}),

    # Two-column layout with Scattermapbox and Scatter plot side by side
    dbc.Row([
        dbc.Col([
            
            html.Div([
                #Titulo grafico 1: 
                html.H4('Map View', style={'textAlign': 'center'}),
                
                #Agrega un slide bar:
                html.Label('Change Layer of map'),
                dcc.Dropdown(id ='boton_change_layer',
                            options = [
                                {'label': 'Satelital View', 'value': 'satellite'},
                                {'label': 'Open Street Map', 'value': 'open-street-map'}
                            ],
                            value = 'open-street-map',
                            style={"width": "60%"} # Adjusted for full width
                ),       
            ], 
            style={'margin-bottom': '20px'}), # Adjust the bottom margin as needed        
               #'height': '10%'
                        #'margin-bottom': '20px'         

            html.Div([

                html.Label('Year of map'),
                dcc.Slider(
                    id="barra_slider",
                    min=2023,max=2030,
                    marks={i: f'Label {i}' if i == 1 else str(i) for i in range(2023, 2031)},
                    value=2023,
                ),  

            ], style={'margin-bottom': '20px'}),   # Adjust the bottom margin as needed
                    # 'margin-bottom': '20px'


            #Código mapa nuevo:
            html.Div([
                #html.H4('Map View', style={'textAlign': 'center'}),

                dcc.Graph(
                    id='scattermapbox',
                    figure=fig,
                    style={'height': '100%', 'width': '100%'}  # Set both height and width to 100%
                )
            ], style={'height': '60vh'}),
                 
        ], width=6),


####################### codigo original mapa: #####################        
        #     #Grafico mapa
        #         html.H4('Map View', style={'textAlign': 'center'}),
        #         #original:
        #         dcc.Graph(
        #         id='scattermapbox',
        #         figure=fig,
        #         style={'height': '100%'})
                
        # ], width=6, style={'height': '50vh'}),

################## end codigo original mapa #######################

############## codigo nuevo scatterplot: #########

        dbc.Col([

            # html.Div([
                    
            # ], style={'margin-bottom': '20px'}),

            # html.Div([
                    
            # ], style={'margin-bottom': '20px'}),    

            html.Div([
            
                html.H4('Graph 01', style={'textAlign': 'center'}),

                dcc.Graph(
                    id='scatter-plot',
                    figure=px.scatter(
                        diabetes_df, x='BloodPressure', y='BMI', color='Age',
                        title='Blood Pressure vs BMI'
                    ),
                    style={'height': '100%', 'width': '100%'}  # Set both height and width to 100%
                )
            ], style={'height': '70vh'}),
        ], width=6),
    ]),

#### end codigo nuevo scatterplot: #####    


########### Codigo antiguo scatterplot: #####################################
    #     #Grafico scatterplot:
    #     dbc.Col([
    #         dcc.Graph(
    #             id='scatter-plot',
    #             figure=px.scatter(diabetes_df, x='BloodPressure', y='BMI', color='Age', title='BloodPressure vs BMI'),
    #             style={'height': '100%'}
    #         )
    #     ],  width=6, style={'height': '50vh'}),
    
    # ]),
############### end código antiguo scatterplot: ########################################


    #html.Br(),
    
    # # Two-column layout with DataTable and Histogram side by side
    # dbc.Row([
    #     dbc.Col([
    #         #Datatable:  
    #         dash_table.DataTable(
    #             id='datatable',
    #             columns=[{'name': col, 'id': col} for col in gapminder_df.columns],
    #             data=gapminder_df.head(12).to_dict('records'),  # Display only 12 rows per page
    #             page_size=12,
    #             style_table={'overflowX': 'auto'}  # Enable horizontal scrolling
    #         )
    #     ], width=6, style={'height': '50vh'}),

    #     dbc.Col([
    #         #Histograma  
    #         dcc.Graph(
    #             id='histogram',
    #             figure=px.histogram(gapminder_df, x='pop', title='Population Histogram')
    #         )
    #     ], width=6, style={'height': '50vh'}),
    # ]),
    
    #Almacena la info de las coordenadas del mapa:
    #Add a dcc.Store to your layout to keep track of the map's zoom and center:

    #-34.08, -73.288
    dcc.Store(id='map-interaction-data', data={'zoom': 3, 'center': {'lat': -34.08, 'lon': -73.288}})

])

#width=6, style={'margin-bottom': '20px'}

@app.callback(
    Output('scattermapbox', 'figure'),
    [Input('boton_change_layer', 'value')],
    [State('map-interaction-data', 'data')]  # Get the stored interaction data
)


def update_map_style(style, interaction_data):
    
    if style == 'open-street-map':
        # Use satellite style
        mapbox_style = "white-bg"
        mapbox_layers = [
            {
                "below": 'traces',
                "sourcetype": "raster",
                "source": [
                    "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                ],
                "sourceattribution": "Powered by Grid and Zero energy consulting",
            }
        ]

     
    if style == 'satellite':
        # Use satellite style
        mapbox_style = "white-bg"
        mapbox_layers = [
            {
                "below": 'traces',
                "sourcetype": "raster",
                "source": [
                    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                ],
                "sourceattribution": "Powered by Grid and Zero energy consulting",
            }
        ]

    # Recreate the figure with the stored zoom and center
    fig = create_figure(mapbox_style, mapbox_layers, interaction_data['zoom'], interaction_data['center'])
    return fig

def create_figure(mapbox_style, mapbox_layers, zoom, center):
    
    #Nuevo: 
    # Create the figure with the mapbox style and layers
    fig = px.scatter_mapbox(
        df_subestaciones_ministerio_geojson, 
        lat=df_subestaciones_ministerio_geojson['geometry'].y,
        lon=df_subestaciones_ministerio_geojson['geometry'].x, 
        hover_name="NOMBRE", 
        hover_data=["PROPIEDAD","TENSION_KV"],
        color_discrete_sequence=["black"],
        height= 500
         
        #zoom=3
    )

    # Asegúrate de que la leyenda se muestre para el scatter plot
    for trace in fig.data:
        trace.showlegend = True
        trace.name = 'Substations (S/E)'  # Asigna un nombre para la leyenda del scatter plot

        # Add lines for 500 kv transmission
    fig2 = px.line_mapbox(geojson_df_500_kv, 
                        lat=lats, 
                        lon=lons, 
                        hover_name=names, 
                        zoom=3, 
                        height=500)
    # Line trace for 500 kv
    line_500_kv = fig2.data[0]
    line_500_kv.showlegend = True
    line_500_kv.name = 'Transmission Lines: 500 kV line'
    line_500_kv.marker.color = 'red'  # Set line color to red
    fig.add_trace(line_500_kv)


    # Add lines for 345 kv transmission
    fig3 = px.line_mapbox(geojson_df_220_kv, 
                        lat=lats_220, 
                        lon=lons_220, 
                        hover_name=names_220,  
                        zoom=3, 
                        height=500)
    # Line trace for 345 kv
    line_345_kv = fig3.data[0]
    line_345_kv.showlegend = True
    line_345_kv.name = 'Transmission Lines: 345 kV line'
    line_345_kv.marker.color = 'yellow'  # Set line color to yellow
    fig.add_trace(line_345_kv)


    # actualiza el color de la línea de 500 kv a rojo.
    fig.update_traces(line=dict(color='red'), selector=1)
    #actualiza el color de la linea de 345 kv a amarillo.
    fig.update_traces(line=dict(color='yellow'), selector=2)    
    
    # Actualiza la configuración del layout para mostrar la leyenda
    fig.update_layout(
        showlegend=True,
        legend_title_text='Legend',  # Título de la leyenda
        legend=dict(
            yanchor="bottom",
            y=0.01,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.5)'  # Fondo semi-transparente para la leyenda
        ),
        mapbox_style=mapbox_style,
        mapbox_layers=mapbox_layers,
        mapbox_zoom=zoom,
        mapbox_center=center,
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    
    #Agrega la imagen del logo de la empresa (Grid and zero energy consulting)
    fig.add_layout_image(
        dict( #"https://i.imgur.com/Dvbcc0N.jpeg"
            source="https://i.imgur.com/Dvbcc0N.jpeg",  # Sustituye con la ruta a tu imagen
            xref="paper", yref="paper",
            x=0.99, y=0.1,
            sizex=0.25, sizey=0.25,  # Tamaño de la imagen en proporción al tamaño del gráfico
            xanchor="right", yanchor="bottom"
        )
    )




    # # Create the figure with the mapbox style and layers
    # fig = px.scatter_mapbox(
    #     df_subestaciones_ministerio_geojson, 
    #     lat=df_subestaciones_ministerio_geojson['geometry'].y,
    #     lon=df_subestaciones_ministerio_geojson['geometry'].x, 
    #     hover_name="NOMBRE", 
    #     hover_data=["PROPIEDAD","TENSION_KV"],
    #     color_discrete_sequence=["black"],
         

    #     #zoom=3
    # )

    # #Add lineas de transmisión de 500 kv:
    # fig2 = px.line_mapbox(geojson_df_500_kv, lat=lats, lon= lons, hover_name= names, height=20)
    # fig.add_trace(fig2.data[0])

    # #Add lineas de transmisión de 345 kv:
    # fig3 = px.line_mapbox(geojson_df_220_kv, lat=lats_220, lon= lons_220, hover_name=names_220, height=20)
    # fig.add_trace(fig3.data[0])


    # # actualiza el color de la línea de 500 kv a rojo.
    # fig.update_traces(line=dict(color='red'), selector=1)
    # #actualiza el color de la linea de 345 kv a amarillo.
    # fig.update_traces(line=dict(color='yellow'), selector=2)


    # # Update the map style
    # fig.update_layout(
    #     mapbox_style=mapbox_style,
    #     mapbox_layers=mapbox_layers,
    #     mapbox_zoom=zoom,
    #     mapbox_center=center,
    #     margin={"r":0,"t":0,"l":0,"b":0}
    # )

    return fig

@app.callback(
    Output('map-interaction-data', 'data'),
    [Input('scattermapbox', 'relayoutData')],
    [State('map-interaction-data', 'data')]
)

def store_map_interaction(relayoutData, interaction_data):
    if relayoutData and 'mapbox.zoom' in relayoutData:
        interaction_data['zoom'] = relayoutData['mapbox.zoom']
    if relayoutData and 'mapbox.center' in relayoutData:
        interaction_data['center'] = relayoutData['mapbox.center']
    return interaction_data


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False,port = 40)
