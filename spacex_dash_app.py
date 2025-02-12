# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
#spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
#server= app.server

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                    ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True,
                                    style={'width': '100%', 'padding': '3px', 'font-size': '20px', 'text-align': 'left'}
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div(dcc.RangeSlider(id='payload-slider',
                                                        min=0, max=10000, step=1000,
                                                        marks={0: '0', 100: '100'},
                                                        value=[min_payload, max_payload])),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        data = filtered_df
        fig = px.pie(data, values='class', 
        names='Launch Site', 
        title='Total Success Launches')
        return fig
    else:
         # Filter for selected site and calculate counts
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        site_counts = site_df.groupby(['class']).size().reset_index(name='count')
        
        fig = px.pie(site_counts, values='count', 
                     names='class', 
                     title=f"Total Success Launches for site {entered_site}")
        fig.update_traces(textinfo='value')  # Show counts instead of percentages
        return fig


# Determine the launch site with the highest success ratio
success_ratio = spacex_df.groupby('Launch Site').apply(
    lambda x: x[x['class'] == 1].shape[0] / x.shape[0] if x.shape[0] > 0 else 0
).reset_index(name='success_ratio')


# Find the launch site with the maximum success ratio
max_success_site = success_ratio.loc[success_ratio['success_ratio'].idxmax()]
print(f"Launch site with highest success ratio: {max_success_site['Launch Site']}, Success Ratio: {max_success_site['success_ratio']}")

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, slider_range):
    low, high = slider_range
    mask = ((spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high))
    filtered_df1 = spacex_df[mask]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df1, x='Payload Mass (kg)', y='class', color='Booster Version Category',
        title='Correlation Between Payload and Success for All Sites')
        return fig
    else:
        filtered_df2 = filtered_df1[filtered_df1['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df2, x='Payload Mass (kg)', y='class', color='Booster Version Category',
        title=f'Correlation Between Payload and Success for Site {entered_site}')
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
