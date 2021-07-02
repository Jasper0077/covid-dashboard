# Import libraries
from datetime import date
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.tools as tls
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

import data_preprocess
from urllib.request import urlopen

Data = data_preprocess.Data()
with urlopen(
        'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/malaysia.geojson') as response:
    mysgeojson = json.load(response)
# Stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Read the dataset
# df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')
data_cul = pd.read_csv('https://raw.githubusercontent.com/wnarifin/covid-19-malaysia/master/covid-19_my.csv')

states = Data.df_monthly_bystate.columns[1:]

# Data Cleaning, extract Malaysia Dataset
# data = df[df.iso_code == 'MYS']

# Fill NaN with zero
# data.isna().values.any()
# data = data.fillna(0)

# Convert datetime
# data['date'] = pd.to_datetime(data['date'])
data_cul.date = pd.to_datetime(data_cul['date'])

# Data preparation
data_second_year = Data.data[Data.data.date >= '2021-01-01']
data_forecast = Data.data[['date', 'total_cases']]
data_vaccination = Data.data[Data.data.date >= '2021-03-02']

# Dataset for Regression with Seaborn
regplot_fig = plt.figure()
with sns.axes_style('darkgrid'):
    ax = sns.regplot(data=data_second_year,
                     x='new_cases',
                     y='new_deaths',
                     color='#2f4b7c',
                     scatter_kws={'alpha': 0.3, 'color': '#DBE6FD'},
                     line_kws={'color': '#ff7c43'})

    ax.set(ylim=(0, 150),
           xlim=(data_second_year.new_cases.min() - 100, 10000),
           ylabel='Daily Deaths',
           xlabel='Daily Confirmed Cases')
regplot_fig_url = tls.mpl_to_plotly(regplot_fig)
regplot_fig_url.update_layout(
    plot_bgcolor='#47597E',
    paper_bgcolor='#47597E',
    hovermode='closest',
    width=500,
    height=400,
    xaxis=dict(
        title='<b>Daily Deaths</b>',
        color='white',
        showline=True,
        showgrid=True,
        showticklabels=True,
        linecolor='white',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=11,
            color='white'
        )
    ),
    yaxis=dict(
        title='<b>Daily Cases</b>',
        color='white',
        showline=True,
        showgrid=True,
        showticklabels=True,
        linecolor='white',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=11,
            color='white'
        )
    ),
    font=dict(
        family='sans-serif',
        size=11,
        color='white'
    )
)

# Dataset for Pie Chart: Active, Recovery and Deaths
data_cul_latest = data_cul.iloc[-1:]
data_cul_latest = data_cul_latest[['total_cases', 'total_deaths', 'total_recover']]
data_cul_latest['active_cases'] = (
        data_cul_latest.total_cases - data_cul_latest.total_deaths - data_cul_latest.total_recover)
data_cul_latest = data_cul_latest[['active_cases', 'total_deaths', 'total_recover']]

# Dataset for Bar Chart
data_global = Data.df[['iso_code', 'continent', 'location', 'date', 'new_cases', 'population']]
data_global = data_global[data_global.continent == 'Asia']
data_global = data_global.groupby(['iso_code', 'location', 'population'], as_index=False).sum('new_cases')
data_global.columns = ['iso_code', 'location', 'population', 'total_cases']
data_global['index'] = ((data_global['total_cases'] / data_global['population']) * 100)

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Set up the app layout
app.layout = html.Div([
    # Title and timestamp
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('digger.png'),
                 id='digger-image',
                 style={
                     "height": "60px",
                     "width": "auto",
                     "margin-bottom": "25px",
                     "margin-left": "50px"
                 },
            )
        ], className="one column"),
        html.Div([
            html.Div([
                html.H3("Data Digger's Covid-19 Dashboard", style={"margin-bottom": "0px", 'color': 'white'}),
                html.H6("Track Malaysia's Covid - 19 Cases", style={"margin-top": "2px", 'color': 'white'}),
            ])
        ], className="one-half column", id="title"),

        html.Div([
            html.H6('Last Updated: ' + str(Data.data.date.iloc[-1].strftime("%B %d, %Y")) + '  00:01 (UTC)',
                    style={'color': 'orange'}),

        ], className="one-third column", id='title1'),

    ], id="header", className="row flex-display", style={"margin-bottom": "25px"}),

    # Numbers of cases, deaths and recovered in Malaysia
    html.Div([
        html.Div([
            html.H6(children='Total Cases',
                    style={
                        'textAlign': 'center',
                        'color': 'white'}
                    ),

            html.P(f"{Data.data['total_cases'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': '#DBE6FD',
                       'fontSize': 40}
                   ),

            html.P('new:  ' + f"{Data.data['new_cases'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': '#DBE6FD',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="create_container four columns",
        ),

        html.Div([
            html.H6(children='Total Deaths',
                    style={
                        'textAlign': 'center',
                        'color': 'white'}
                    ),

            html.P(f"{Data.data['total_deaths'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': 'red',
                       'fontSize': 40}
                   ),

            html.P('new:  ' + f"{Data.data['new_deaths'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': 'red',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="create_container four columns",
        ),

        html.Div([
            html.H6(children='Total Recovery',
                    style={
                        'textAlign': 'center',
                        'color': 'white'}
                    ),

            html.P(f"{data_cul['total_recover'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': '#E5D549',
                       'fontSize': 40}
                   ),

            html.P('new:  ' + f"{data_cul['recover'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': '#E5D549',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="create_container four columns",
        )
    ], className='row flex-display'),

    # Asian comparison and latest pie chart, vaccination pie chart
    html.Div([
        # Asian comparison
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='column',
                    options=[
                        {'label': 'Total Cumulative Cases', 'value': 'total_cases'},
                        {'label': 'Population', 'value': 'population'},
                        {'label': 'Infection Rate', 'value': 'index'}
                    ],
                    value='total_cases'
                ),
                dcc.Dropdown(
                    id='ranking',
                    options=[
                        {'label': '1 - 10', 'value': 10},
                        {'label': '11 - 20', 'value': 20},
                        {'label': '21 - 30', 'value': 30},
                        {'label': '31 - 40', 'value': 40},
                        {'label': '41 - 50', 'value': 50},
                    ],
                    value=10,
                    style={
                        'margin-top': '4px'
                    }
                ),
            ]),

            html.Div([
                dcc.Graph(
                    id='bar',
                )
            ],
                style={
                    'width': '80%',
                    'margin-left': '-3px'
                }
            )
        ], className='create_container six columns'),

        # Latest pie chart
        html.Div([
            dcc.Graph(
                id='pie-case'
            )
        ], className='create_container three columns'),

        # Vaccination pie chart
        html.Div([
            html.Div([
                dcc.DatePickerSingle(
                    id='vaccine_date',
                    min_date_allowed=date(2021, 3, 1),
                    max_date_allowed=data_vaccination.date.max(),
                    initial_visible_month=date(2021, 6, 25),
                    date=date(2021, 6, 25)
                )
            ]

            ),
            dcc.Graph(
                id='fig_vaccine'
            )
        ], className='create_container three columns'),

    ], className='row flex-display'),

    # Choropleth Chart
    html.Div([
        html.Div([
            html.H4(
                'Changes of Cumulative Confirmed cases of Each States in Malaysia',
                style={
                    'text-align': 'center',
                    'color': 'white',
                    'font-size': '20px'
                }),
            dcc.Graph(id="choropleth")
        ], className='create_container twelve columns')
    ], className='row flex-display'),

    # Line Chart and Bar Chart
    html.Div([
        # Line Chart
        html.Div([
            html.Div([
                dcc.Checklist(
                    id="check_item",
                    options=[{'label': 'Daily Cases', 'value': 'new_cases,New Cases,Number of New Cases'},
                             {'label': 'Daily Deaths', 'value': 'new_deaths,New Deaths,Number of New Deaths'},
                             {'label': 'Stringency Index',
                              'value': 'stringency_index,Stringency Index,Malaysia Stringency Index'}],
                    value=['new_cases,New Cases,Number of New Cases',
                           'new_deaths,New Deaths,Number of New Deaths']

                ),
            ], className='checkbox_container'),
            dcc.Graph(id="line_graph")
        ], className='create_container six columns'),
        # Bar Chart
        html.Div([
            dcc.Dropdown(
                id="select_population_type",
                options=[{'label': 'Population Number', 'value': 'Population Number'},
                         {'label': 'Population Density', 'value': 'Population Density'}],

                value='Population Number'
            ),
            dcc.Graph(id="bar_graph")

        ], className='create_container six columns'),
    ], className='row flex-display'),

    # Heatmap and Prediction
    html.Div([
        # Heat Map
        html.Div([
            dcc.Dropdown(
                id="check_states",
                options=[{'label': x, 'value': x}
                         for x in states],
                value=states,
                multi=True,
                clearable=False
            ),
            dcc.Graph(id="heatmap_monthly_bystate")
        ], className='create_container seven columns'),

        # Prediction
        html.Div([
            html.Div([
                html.H4(
                    "Prediction on Malaysia Daily Deaths from Daily Cases",
                    style={
                        'text-align': 'center',
                        'color': 'white',
                        'font-size': '20px',
                        'margin-bottom': '20px'
                    }
                ),
            ]),
            dcc.Graph(
                id='seaborn-graph',
                figure=regplot_fig_url,
                style={
                    'display': 'flex'
                }
            )
        ], className='create_container five columns'),

    ], className='row flex-display'),
])

# Option Columns
options = [
    {'label': 'Total Cumulative Cases', 'value': 'total_cases'},
    {'label': 'Population', 'value': 'population'},
    {'label': 'Infection Rate', 'value': 'index'}
]


# Set the callback function

# Asian comparison
@app.callback(
    Output(component_id='bar', component_property='figure'),
    Input(component_id='column', component_property='value'),
    Input(component_id='ranking', component_property='value'))
def update_confirmed(column, ranking):
    data_global.sort_values(column, ascending=False, inplace=True)
    selected_data = data_global[ranking - 10:ranking]
    malaysia_data = data_global[data_global.iso_code == 'MYS']
    got_malaysia = False
    for i, r in selected_data.iterrows():
        if r.iso_code == 'MYS':
            got_malaysia = True
            break
    if not got_malaysia:
        selected_data = selected_data.append(malaysia_data, ignore_index=True)
    selected_data.sort_values(column, ascending=False, inplace=True)
    # for i, r in selected_data.iterrows():
    #     print(r.iso_code)
    # fig = px.bar(x=selected_data.location,  # countries name in Asia
    #              y=selected_data[column],  # Total recent confirmed cases
    #              title='Total Cases (Asia countries)',
    #              hover_name=selected_data.location,
    #              color=selected_data[column],
    #              color_continuous_scale='Agsunset')
    y_title = [f"{o['label']}" for o in options if column == o["value"]]
    # print(y_title)
    # fig.update_layout(xaxis_title='Country',
    #                   yaxis_title=column,
    #                   coloraxis_showscale=False)
    return {
        'data': [go.Bar(x=selected_data.location,
                        y=selected_data[column],
                        name='Daily confirmed',
                        marker=dict(
                            color='orange'),
                        )],
        'layout': go.Layout(
            plot_bgcolor='#47597E',
            paper_bgcolor='#47597E',
            hovermode='x',
            title={
                'text': f'Top {ranking - 10}-{ranking} {y_title[0]} in Asia Compared to Malaysia',
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': 'white',
                'size': 17
            },
            margin=dict(r=30),
            xaxis=dict(
                title='<b>Country</b>',
                color='white',
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='white',
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=11,
                    color='white'
                )
            ),
            yaxis=dict(
                title='<b>Daily confirmed Cases</b>',
                color='white',
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='white',
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=11,
                    color='white'
                )
            ),

            legend={
                'orientation': 'h',
                'bgcolor': '#47597E',
                'xanchor': 'center', 'x': 0.5, 'y': -0.03
            },
            font=dict(
                family='sans-serif',
                size=11,
                color='white'
            )
        )
    }


# Cases Pie Chart
@app.callback(
    Output(component_id='pie-case', component_property='figure'),
    [Input("select_population_type", "value")]
)
def update_confirmed(none):
    colors = ['#1768AC', '#E5D549', '#2541B2']
    return {
        'data': [go.Pie(labels=['Active Cases', 'Total Deaths', 'Total Recovered'],
                        values=data_cul_latest.values[0],
                        marker=dict(colors=colors),
                        textinfo='label+value',
                        textfont=dict(size=11),
                        hole=0.6,
                        rotation=35
                        )],
        'layout': go.Layout(
            plot_bgcolor='#47597E',
            paper_bgcolor='#47597E',
            hovermode='closest',
            title={
                'text': 'Latest Cases in Malaysia',
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': 'white',
                'size': 20
            },
            legend={
                'orientation': 'h',
                'bgcolor': '#47597E',
                'xanchor': 'center', 'x': 0.5, 'y': -0.07
            },
            font=dict(
                family='sans-serif',
                size=11,
                color='white'
            )
        )
    }


# Vaccination Pie Chart
@app.callback(
    Output(component_id='fig_vaccine', component_property='figure'),
    Input(component_id='vaccine_date', component_property='date')
)
def update_confirmed(vaccine_date):
    data_vaccination_recent = data_vaccination[data_vaccination.date == vaccine_date]
    data_vaccination_recent[
        'unvaccinated'] = -data_vaccination_recent.people_vaccinated + data_vaccination_recent.population
    data_vaccination_recent[
        '1st_dose_vaccinated'] = data_vaccination_recent.people_vaccinated - data_vaccination_recent.people_fully_vaccinated
    data_vaccination_recent = data_vaccination_recent[
        ['people_fully_vaccinated', 'unvaccinated', '1st_dose_vaccinated']]
    colors = ['#DBE6FD', '#293B5F', '#B2AB8C']
    return {
        'data': [go.Pie(labels=['Fully Vaccinated', 'Unvaccinated', '1st Dose Vaccinated'],
                        values=data_vaccination_recent.values[0],
                        marker=dict(colors=colors),
                        textinfo='label+value',
                        textfont=dict(size=11),
                        # names=['2nd Dosed Population', 'Unvaccinated Population', '1st Dosed Only Population'],
                        hole=0.6,
                        rotation=35
                        )],
        'layout': go.Layout(
            plot_bgcolor='#47597E',
            paper_bgcolor='#47597E',
            hovermode='closest',
            title={
                'text': 'Vaccination Rate in Malaysia',
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': 'white',
                'size': 20
            },
            legend={
                'orientation': 'h',
                'bgcolor': '#47597E',
                'xanchor': 'center', 'x': 0.5, 'y': -0.07
            },
            font=dict(
                family='sans-serif',
                size=11,
                color='white'
            )
        )
    }


# Choropleth chart
@app.callback(
    Output("choropleth", "figure"),
    [Input("select_population_type", "value")]
)
def update_confirmed(none):
    fig = px.choropleth(Data.df_cumulative_restruct,
                        geojson=mysgeojson,
                        height=450,
                        width=1200,
                        locations="state", featureidkey="properties.name", color="cumulative case",
                        color_continuous_scale="plotly3",
                        labels={'cumulative case': 'Cumulative Case'},
                        animation_frame="year_month",
                        hover_name="state")
    fig.update_geos(fitbounds="geojson", visible=False)
    fig.update_layout(
        # margin={"r": 10, "t": 0, "l": 10, "b": 0},
        plot_bgcolor='#47597E',
        paper_bgcolor='#47597E',
        font=dict(
            family='sans-serif',
            size=13,
            color='white'
        )
    )

    return fig


# Bar Chart
@app.callback(
    Output("bar_graph", "figure"),
    [Input("select_population_type", "value")]
)
def update_bar(population_type):
    states = Data.df_case_with_pop['State']
    states_population = Data.df_case_with_pop['Population']
    if population_type == "Population Number":
        states_population = Data.df_case_with_pop['Population']
    elif population_type == "Population Density":
        states_population = Data.df_case_with_pop['Population Density']
    states_cum_case = Data.df_case_with_pop['Cumulative Case']

    fig = go.Figure()
    fig.add_trace(go.Bar(x=states,
                         y=states_population,
                         name=population_type,
                         marker_color='#DBE6FD',
                         yaxis='y', offsetgroup=1))
    fig.add_trace(go.Bar(x=states,
                         y=states_cum_case,
                         name='Cumulative Case',
                         marker_color='orange',
                         yaxis='y2', offsetgroup=2))

    fig.update_layout(
        plot_bgcolor='#47597E',
        paper_bgcolor='#47597E',
        hovermode='x',
        title={
            'text': 'Malaysia Cumulative Cases against Population by States',
            'y': 0.93,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        titlefont={
            'color': 'white',
            'size': 20
        },
        xaxis=dict(
            title='<b>States</b>',
            color='white',
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='white',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=11,
                color='white'
            )
        ),
        yaxis=dict(
            title=f'<b>{population_type}</b>',
            color='white',
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='white',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=11,
                color='white'
            )
        ),
        yaxis2=dict(
            title='<b>Covid-19 Cumulative Cases </b>',
            color='white',
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='white',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=11,
                color='white'
            ),
            overlaying='y',
            side='right'
        ),

        legend={
            'x': 0.1,
            'y': 1.15,
            'bgcolor': '#47597E',
            'xanchor': 'center'
        },
        font=dict(
            family='sans-serif',
            size=11,
            color='white'
        ),
        xaxis_tickangle=-45,
        barmode='group',
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )

    return fig


# Line Chart
@app.callback(
    Output("line_graph", "figure"),
    [Input("check_item", "value")]
)
def update_line_case_deaths_stringency(checked_item):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    temp1 = []
    temp2 = []
    if len(checked_item) == 0:
        # Add traces
        fig.add_trace(
            go.Scatter(x=Data.data.date, y=Data.data['new_cases'], name="New Cases"),
            secondary_y=False,
        )
    else:
        # Add traces
        temp1 = checked_item[0].split(",")
        fig.add_trace(
            go.Scatter(x=Data.data.date, y=Data.data[temp1[0]], name=temp1[1]),
            secondary_y=False,
        )

        if len(checked_item) == 2:
            temp2 = checked_item[1].split(",")
            fig.add_trace(
                go.Scatter(x=Data.data.date, y=Data.data[temp2[0]], name=temp2[1]),
                secondary_y=True,
            )

    # Add figure title
    fig.update_layout(
        # title_text="Malaysia New Case and Death",
        plot_bgcolor='#47597E',
        paper_bgcolor='#47597E',
        hovermode='x',
        title={
            'text': "Malaysia Daily Cases vs Daily Deaths vs Stringency Index",
            'y': 0.93,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        titlefont={
            'color': 'white',
            'size': 20
        },
        xaxis=dict(
            # title='<b>States</b>',
            color='white',
            showline=True,
            showticklabels=True,
            linecolor='white',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=11,
                color='white'
            )
        ),
        yaxis=dict(
            # title=f'<b>{population_type}</b>',
            color='white',
            showline=True,
            showticklabels=True,
            linecolor='white',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=11,
                color='white'
            )
        ),
        yaxis2=dict(
            # title=f'<b>{population_type}</b>',
            color='white',
            showline=True,
            showticklabels=True,
            linecolor='white',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=11,
                color='white'
            )
        ),
        font=dict(
            family='sans-serif',
            size=11,
            color='white'
        ),
    )

    # Set x-axis title
    fig.update_xaxes(title_text="<b>Date</b>")

    # Set y-axes titles
    # fig.update_yaxes(title_text="<b>Number of New Cases</b>", secondary_y=False)
    # fig.update_yaxes(title_text="<b>Number of New Deaths</b>", secondary_y=True)
    if len(temp1):
        fig.update_yaxes(title_text="<b>" + temp1[2], secondary_y=False)
        if len(temp2):
            fig.update_yaxes(title_text="<b>" + temp2[2], secondary_y=True)
    else:
        fig.update_yaxes(title_text="<b>Number of New Cases</b>", secondary_y=False)

    return fig


# Heatmap Monthly by State
@app.callback(
    Output("heatmap_monthly_bystate", "figure"),
    [Input("check_states", "value")]
)
def update_heatmap_monthly_bystate(checked_states):
    dates = Data.df_monthly_bystate['year_month']
    display_states = checked_states
    monthly_cases = Data.df_monthly_bystate[checked_states].T

    fig = go.Figure(data=go.Heatmap(
        x=dates,
        y=display_states,
        z=monthly_cases,
        colorscale='turbo'))

    fig.update_layout(
        xaxis_nticks=36,
        plot_bgcolor='#47597E',
        paper_bgcolor='#47597E',
        hovermode='x',
        title={
            'text': 'Monthly Increased Cases by State',
            'y': 0.93,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        titlefont={
            'color': 'white',
            'size': 20
        },
        margin=dict(r=50),
        xaxis=dict(
            title='<b>Date</b>',
            color='white',
            showline=False,
            showgrid=False,
            showticklabels=True,
            linecolor='white',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=11,
                color='white'
            )
        ),
        yaxis=dict(
            title='<b>States</b>',
            color='white',
            showline=False,
            showgrid=False,
            showticklabels=True,
            linecolor='white',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=11,
                color='white'
            )
        ),
        font=dict(
            family='sans-serif',
            size=11,
            color='white'
        )
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
