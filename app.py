import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import altair as alt
from vega_datasets import data


# Initializing dash app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'SHARE data visualisation'

# Adding Heroku server object
server = app.server

# Preparing data
state_map = alt.topo_feature(data.us_10m.url, 'states')
data = pd.read_csv('https://raw.githubusercontent.com/UBC-MDS/DSCI532-Group16/main/data/processed/processed_survey.csv')

#States dataframe for filter
df_states = data[['state_fullname', 'state']].drop_duplicates(subset=['state_fullname','state']).dropna()
df_states = df_states.sort_values(by='state_fullname')


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H3("Properties", className="display-5"),
        html.Hr(),
        # html.P(
        #     ""
        # ),

        html.Br(),
        # Variable selector
        html.H4(html.Label(['Variable Selection'])), 
        dcc.Dropdown(
            id = 'variable_selector',
            options=[{"label": "gdp", "value": "gdp"},
                     {"label": "computer use", "value": "computer_use"},
                     {"label": "computer skills", "value": "computer_skills"},
                     {"label": "mental fatigue", "value": "mental_fatigue"},
                     {"label": "physical fatigue", "value": "physical_fatigue"},
                     {"label": "energy", "value": "energy"}]
            value='computer us', 
            multi=False,
            # style={'height': '30px', 'width': '250px'}
            ),                    
                
        html.Br(),
        # Age Slider
        html.H4(html.Label(['Age'])),
        dcc.RangeSlider(id = 'age_slider', min = 1939, max = 1978, value = [1939,1978], 
            marks = {1939:'1939', 1948:'1948', 1963:'1963', 1978:'1978'}),
        
        html.Br(),
        # Gender Filter Checklist
        html.H4(html.Label(['Gender'])),
        dcc.Checklist(
            id = 'gender_checklist',
            options = [
                {'label' : 'Male', 'value' : 'Male'},
                {'label' : 'Female  ', 'value' : 'Female'}],
            value = ['Male', 'Female'],
            labelStyle = dict(display='block')
        ),
        html.Br(),
        # Country Radio buttons
        html.H4(html.Label(['Country'])),
        dcc.RadioItems(
            id = 'country_radioitems',
            options = [
                {'label' : 'Austria', 'value' : 'Austria'},
                {'label' : 'Germany', 'value' : 'Germany'},
                {'label' : 'Sweden', 'value' : 'Sweden'},
                {'label' : 'Spain', 'value' : 'Spain'},
                {'label' : 'Italy', 'value' : 'Italy'},
                {'label' : 'France', 'value' : 'France'},
                {'label' : 'Denmark', 'value' : 'Denmark'},
                {'label' : 'Greece', 'value' : 'Greece'},
                {'label' : 'Switzerland', 'value' : 'Switzerland'},
                {'label' : 'Belgium', 'value' : 'Belgium'},
                {'label' : 'Czech Republic', 'value' : 'Czech Republic'},
                {'label' : 'Poland', 'value' : 'Poland'}],
            value = 'Denmark',            
            labelStyle = dict(display='block')
        )

    ],
    style=SIDEBAR_STYLE,
)


CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

content = html.Div([
           html.H2('Employee Mental Health Survey in the US'),
            dbc.Tabs([
                # Tab 1
                dbc.Tab([

                    dbc.Row(
                            dbc.Col(
                                # Map plot
                                html.Iframe(
                                    id = 'map_frame', 
                                    style = {'border-width' : '0', 'width' : '100%', 'height': '400px'}),
                                style={'margin-bottom':'50px', 'textAlign':'center'} ,                                    
                                width=True, 
                                ),style={'textAlign': 'center'}
                    ),

                    dbc.Row([
                        dbc.Col(
                            #Options Barplot
                            html.Iframe(
                                id = 'options_barplot', 
                                style = {'border-width' : '0', 'width' : '100%', 'height': '100%'})
                        ), 
                    ]),

                    dbc.Row([
                        dbc.Col(
                            #Discuss mental issues with supervisor boxplot
                            html.Iframe(
                                id = 'iframe_discuss_w_supervisor', 
                                style = {'border-width' : '0', 'width' : '100%', 'height': '100%'}),            
                        )
                    ]),   
                      
                    ],
                    label = 'Map visualisation'),

                
                Tab 2
                dbc.Tab('Other text', label = 'Network Vosualisation')
            ])], 
            id="page-content", 
            style=CONTENT_STYLE)


app.layout = html.Div([
    sidebar,
    content,
])

@app.callback(
    Output('options_barplot', 'srcDoc'),
    Input('age_slider', 'value'),
    Input('state_selector','value'),
    Input('gender_checklist', 'value'),
    Input('self_emp_checklist', 'value'))
def plot_options_bar(age_chosen, state_chosen, gender_chosen, self_emp_chosen):
    chart = alt.Chart(data[(data['Age'] >= age_chosen[0]) 
    & (data['Age'] <= age_chosen[1]) 
    & (data['state'] == state_chosen )
    & (data['Gender'].isin(gender_chosen))
    & (data['self_employed'].isin(self_emp_chosen))], 
    title = "Do you know the options for mental healthcare your employer provides?").mark_bar().encode(
        x = alt.X('count()'),
        y = alt.Y('care_options', sort = '-x', title = ""))

    return chart.to_html()


@app.callback(
    Output('iframe_discuss_w_supervisor', 'srcDoc'),
    Input('age_slider', 'value'),
    Input('state_selector','value'),
    Input('gender_checklist', 'value'),
    Input('self_emp_checklist', 'value'))
def plot_discuss_w_supervisor(age_chosen, state_chosen, gender_chosen, self_emp_chosen):
    filtered_data = data[(data['Age'] >= age_chosen[0]) 
    & (data['Age'] <= age_chosen[1]) 
    & (data['state'] == state_chosen )
    & (data['Gender'].isin(gender_chosen))
    & (data['self_employed'].isin(self_emp_chosen))]
    supervisor_boxplot = alt.Chart(filtered_data, 
        title='Would employee be willing to discuss mental health issues with supervisor?').mark_boxplot().encode(
            x=alt.X('Age',  scale=alt.Scale(domain=[18, 80])), 
            y=alt.Y('supervisor',title='')                                
            )
    supervisor_means = (alt.Chart(filtered_data)).mark_circle(color='white').encode( x='mean(Age)', y='supervisor')
    chart = (supervisor_boxplot + supervisor_means)
    return chart.to_html()


map_click = alt.selection_multi()


@app.callback(
    Output('map_frame', 'srcDoc'),
    Input('age_slider', 'value'),
    Input('gender_checklist', 'value'),
    Input('self_emp_checklist', 'value'))
def plot_map(age_chosen, gender_chosen, self_emp_chosen):

    filtered_data = data[(data['Age'] >= age_chosen[0]) 
    & (data['Age'] <= age_chosen[1])
    & (data['Gender'].isin(gender_chosen))
    & (data['self_employed'].isin(self_emp_chosen))]

    frequencydf = filtered_data.groupby('id')['has_condition'].transform('sum')
    data['Mental_health_count'] = frequencydf
    
    map = (alt.Chart(state_map, 
        title = 'Frequency of mental health condition').mark_geoshape().transform_lookup(
        lookup='id',
        from_=alt.LookupData(data, 'id', ['Mental_health_count']))
        .encode(
        color='Mental_health_count:Q',
        opacity=alt.condition(map_click, alt.value(1), alt.value(0.2)),
        tooltip=['state:N', 'Mental_health_count:Q'])
        .add_selection(map_click)
        .project(type='albersUsa')).properties(
                                width=700,
                                height=350
                            )
    return map.to_html()

if __name__ == '__main__':
    app.run_server(debug = True)

