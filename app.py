import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import altair as alt
from vega_datasets import data


# Initializing dash apps
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'SHARE data visualisation'

# Adding Heroku server object
server = app.server

# Preparing data
countries = alt.topo_feature(data.world_110m.url, 'countries')
data = pd.read_csv('./data/share_data.csv',index_col=0)
country_id = {'Austria':40,'Belgium':56,'Czech Republic':203,'Denmark':208,
              'France':250,'Germany':276,'Greece':300,'Italy':380,'Poland':616,
              'Spain':724,'Sweden':752,'Switzerland':756}

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
        html.H4(html.Label(['Indicator Selection'])),
        dcc.Dropdown(
            id = 'variable_selector',
            options=[#{"label": "gdp", "value": "gdp"},
                     {"label": "Internet use", "value": "UseWWW"},
                    #  {"label": "computer skills", "value": "skills"},
                     {"label": "Mental fatigue", "value": "MentalFatigue"},
                     {"label": "Physical fatigue", "value": "PhysicalFatigue"},
                    #  {"label": "energy", "value": "energy"},
                    ],
            value='UseWWW',
            multi=False,
            # style={'height': '30px', 'width': '250px'}
            ),
        html.P('Display visualisation of respondents answered \'Yes\' if you select:'),
        html.P('Internet use: During the past 7 days, have you used the Internet?'),
        html.P('Mental Fatigue: In the last month, have you had too little energy?'),
        html.P('Physical Fatigue: Are you bothered by frailty, fatigue?'),
        html.Br(),
        html.H4('Filters'),
        html.Br(),
        # Age Slider
        html.H5(html.Label(['Age'])),
        html.P('Please set a range of age'),
        dcc.RangeSlider(id = 'age_slider', min = 50, max = 101, value = [50,101],
            marks = {50:'50', 65:'65', 80:'80', 110:'>80'}),
        
        html.Br(),
        # Gender Filter Checklist
        html.H5(html.Label(['Gender'])),
        html.P('Please select at least one gender'),
        dcc.Checklist(
            id = 'gender_checklist',
            options = [
                {'label' : 'Male', 'value' : 'Male'},
                {'label' : 'Female  ', 'value' : 'Female'}],
            value = ['Male', 'Female'],
            labelStyle = dict(display='block')
        ),

    ],
    style=SIDEBAR_STYLE,
)


CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

content = html.Div([
           html.H2('SHARE data visualisation'),
            html.Div([
                html.P('Data Source: Survey of Health, Aging and Retirement in Europe (SHARE), Wave 7 (n=11008), release 7.1.1 (Börsch-Supan, A., 2019), our own calculation.')
            ]),
            dbc.Tabs([
                # Tab 1
                dbc.Tab([

                    dbc.Row(
                            dbc.Col(
                                # Map plot
                                html.Iframe(
                                    id = 'map_frame',
                                    style = {'border-width' : '0', 'width' : '100%', 'height': '1200px'}),
                                style={'margin-bottom':'50px', 'textAlign':'center'} ,
                                width=True,
                                ),style={'textAlign': 'center'}
                    ),
                    ],
                    label = 'Map visualisation'),
            ])],
            id="page-content",
            style=CONTENT_STYLE)


app.layout = html.Div([
    sidebar,
    content,
])

map_click = alt.selection_multi(fields=['Country'])
@app.callback(
    Output('map_frame', 'srcDoc'),
    Input('age_slider', 'value'),
    Input('gender_checklist', 'value'),
    Input('variable_selector', 'value'))
def plot_map(age_chosen, gender_chosen, var_chosen):

    filtered_data = data[(data['Age'] >= age_chosen[0])
    & (data['Age'] <= age_chosen[1])
    & (data['Gender'].isin(gender_chosen))]
    ct = pd.crosstab(filtered_data.Country, filtered_data[var_chosen], normalize='index')
    ct = ct.reset_index()
    ct['id'] = ct.apply(lambda x: country_id[x['Country']], axis=1)
    if var_chosen == 'PhysicalFatigue':
        ct = ct.rename(columns={'Selected': 'Percentage'})
    else:
        ct = ct.rename(columns={'Yes': 'Percentage'})
    map = (alt.Chart(countries,
        title = 'Map visualisation of selected indicator').mark_geoshape().transform_lookup(
        lookup='id',
        from_=alt.LookupData(ct, 'id', ['Percentage','Country']))
        .encode(
        color='Percentage:Q',
        opacity=alt.condition(map_click, alt.value(1), alt.value(0.2)),
        tooltip=[
        alt.Tooltip('Country:N', title="Country"),
        alt.Tooltip('Percentage:Q', title="Percentage", format='.1%')
        ])
        # tooltip=['Country:N', 'Percentage:Q'])
        .add_selection(map_click)
        .project(
            type= 'mercator',
            scale=400, translate=[150, 550]
            # center=[10,50],
            # clipExtent=[[0,300],[400,700]]
        )).properties(
            width=400, height=300
        )

    chart = alt.Chart(ct,
                      title='Bar chart of selected indicator').mark_bar().encode(
        x='Percentage',
        opacity=alt.condition(map_click, alt.value(1), alt.value(0.2)),
        tooltip=[
        alt.Tooltip('Country:N', title="Country"),
        alt.Tooltip('Percentage:Q', title="Percentage", format='.1%')
        ],
        color='Percentage',
        y=alt.Y('Country',sort='x')
        ).add_selection(map_click
        ).properties(width=200, height=150)
    board = chart & map
    return board.to_html()





# @app.callback(
#     Output('iframe_discuss_w_supervisor', 'srcDoc'),
#     Input('age_slider', 'value'),
#     Input('state_selector','value'),
#     Input('gender_checklist', 'value'),
#     Input('self_emp_checklist', 'value'))
# def plot_discuss_w_supervisor(age_chosen, state_chosen, gender_chosen, self_emp_chosen):
#     filtered_data = data[(data['Age'] >= age_chosen[0]) 
#     & (data['Age'] <= age_chosen[1]) 
#     & (data['state'] == state_chosen )
#     & (data['Gender'].isin(gender_chosen))
#     & (data['self_employed'].isin(self_emp_chosen))]
#     supervisor_boxplot = alt.Chart(filtered_data, 
#         title='Would employee be willing to discuss mental health issues with supervisor?').mark_boxplot().encode(
#             x=alt.X('Age',  scale=alt.Scale(domain=[18, 80])), 
#             y=alt.Y('supervisor',title='')                                
#             )
#     supervisor_means = (alt.Chart(filtered_data)).mark_circle(color='white').encode( x='mean(Age)', y='supervisor')
#     chart = (supervisor_boxplot + supervisor_means)
#     return chart.to_html()






#
# @app.callback(
#     Output('map_frame', 'figure'),
#     Input('age_slider', 'value'),
#     Input('gender_checklist', 'value'),
#     Input('variable_selector', 'value'))
# def plot_map(age_chosen, gender_chosen, var_chosen):
#
#     filtered_data = data[(data['yrbirth'] >= age_chosen[0])
#     & (data['yrbirth'] <= age_chosen[1])
#     & (data['gender'].isin(gender_chosen))]
#
#     ct = pd.crosstab(filtered_data.country, filtered_data[var_chosen], normalize='index')
#     ct = ct.reset_index()
#     fig = go.Figure(
#         data=[go.Choropleth(
#             locationmode='country names',
#             locations=ct['country'],
#             z=ct['Yes'].astype(float),
#             colorscale='Reds',
#         )]
#     )
#
#     fig.update_layout(
#         title_text="Share map",
#         title_xanchor="center",
#         title_font=dict(size=24),
#         title_x=0.5,
#         geo=dict(scope='europe'),
#         margin=dict(l=0, r=0, t=0, b=0))
#
#     return fig

if __name__ == '__main__':
    app.run_server(debug = True)

