import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd

PATH_TO_CSV = "csv_dashboard"

app_dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

server = app_dash.server

# подгружаем данные для построения графиков по индексам
index_history = pd.read_csv(f'{PATH_TO_CSV}/index_doc_count.csv')

# подгружаем данные по необновленным историческим данным
df_not_upd = pd.read_csv(f'{PATH_TO_CSV}/not_updates_files.csv')

# подгружаем данные по случайным брендам
df_random_brands = pd.read_csv(f'{PATH_TO_CSV}/random_brands.csv').tail(22)


def get_last_value(index_name):

    """
    Функция возвращает актуальное количество записей в нужном индексе

    Args:
        index_name(str): имя индекса Elasticsearch.

    Returns:
        int: актуальное количество записей.
    """

    return index_history[index_history['es_index'] == index_name].tail(1)['count_docs'].values[0]


def generate_card(index_name):

    """
    Функция для генерации карточки с наименованием индекса и количеством записей в нем

    Args:
        index_name(str): название индекса.
    Returns:
        dbc.Card: сгенерированная карточка.
    """

    card = dbc.Card([
        dbc.CardHeader(index_name, style={'text-align': 'center',
                                          'text-transform': 'uppercase'}),
        dbc.CardBody(
            [html.H5(f"Количество уникальных id", style={'text-align': 'center',
                                                         'text-transform': 'uppercase',
                                                         'padding-bottom': "60px",
                                                         'padding-top': "30px"
                                                         }),
             html.H1(f"{get_last_value(index_name)}", style={'text-align': 'center',
                                                             'text-transform': 'uppercase',
                                                             }),
             ]
            , style={"height": "300px"}, className="align-items-center")
    ], color="#e76f51", inverse=True)
    return card


def plot_line(index_history, index_name):

    """
    Функция получает датафрейм и имя индекса, возвращает график

    Args:
        index_history (pandas.DataFrame): история изменений индекса.

    Returns:
        plotly.graph_objects.Figure: график изменения записей в индексе
    """

    # выбираем все данные для построения графика
    dff = index_history[index_history['es_index'] == index_name]

    fig = go.Figure()
    # Create and style traces
    fig.add_trace(go.Scatter(x=dff['date'], y=dff['count_docs'], name=f'{index_name}',
                             line=dict(color='#e76f51', width=4),
                             hovertemplate='Записей: %{y}<extra></extra>' + '<br>Дата: %{x}'))
    fig.update_layout(template="simple_white",
                      title=f'Изменение записей в индексе {index_name}',
                      title_x=0.5,
                      xaxis_title='Дата',
                      yaxis_title='Количество записей',
                      )
    fig.update_xaxes(
        tickformat='%d.%m.%y')

    return fig


def plot_all_data(df_plot):

    """
    График для отображения процентов не обновленных историй

    Args:
        df_plot (pandas.DataFrame): исходный датафрейм с историями для вывода на график.

    Returns:
        plotly.graph_objects.Figure: график с процентами необновленных историй.
    """

    # сортируем датафрейм по дате
    data = df_plot.sort_values(by='date').tail(60)

    # нужные данные получены - строим график
    fig = go.Figure()

    # для каждого типа истории добавляем свою кривую
    colors_lines = ['#ef476f', '#2a9d8f', '#ffd166', '#264653', '#0077b6']

    for no, nm in enumerate(['tr_', 'pr_', 'lf_', 'pos_', 'tags_']):
        if nm == 'tr_':
            name_leg = 'tradecount_history'
        elif nm == 'pr_':
            name_leg = 'prices'
        elif nm == 'lf_':
            name_leg = 'leftovers'
        elif nm == 'pos_':
            name_leg = 'position_in_category'
        elif nm == 'tags_':
            name_leg = 'tags'

        fig.add_trace(go.Scatter(
            name=name_leg,
            x=data['date'],
            y=data[nm + 'mean'],
            text=[f'{name}%' for name in round(data[nm + 'mean'], 2)],
            textposition='top right',
            textfont=dict(
                family="sans serif",
                size=8),
            mode='lines+markers',
            line=dict(color=colors_lines[no]),
            hovertemplate='%{y}%<extra></extra>' + '<br>Дата: %{x}',
        ))

        fig.update_yaxes(
            title_text="Процент",
            title_standoff=15,
            rangemode="tozero")

        fig.update_xaxes(
            title_text="Дата",
            title_standoff=15,
            tickformat='%d.%m.%y')

    fig.update_layout(
        title_text=f"Процент товаров с необновленной историей показателей<br>(случайная выборка) за последний месяц",
        title_x=0.5,
        showlegend=True,
        template="simple_white",
        height=500
    )

    return fig


def plot_random_brands(data):

    """
    График процента отсутствующих товаров из случайных брендов

    Args:
        data (pandas.DataFrame): датафрейм с данными по отсутствующим товарам.

    Returns:
        plotly.graph_objects.Figure: график с процентом отсутствующих товаров.
    """

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        name='% отсутствующих товаров',
        x=data['date'],
        y=data['mean_no'],
        error_y=dict(type='data', symmetric=False,
                     array=data['max'] - data['mean_no'],
                     arrayminus=data['mean_no'] - data['min'],
                     color="rgba(213, 86, 7, 0.7)"),
        # text=[f'{name}%' for name in data['mean_no']],
        hovertemplate='%{y}%<extra></extra>' + '<br>Дата: %{x}',
        # textposition="top right",
        # textfont=dict(
        # family="sans serif",
        # size=8),
        mode='lines+markers',
        line=dict(color='rgb(217, 95, 2)')

    ))

    fig.add_trace(go.Scatter(
        name='Отклонение вниз',
        x=data['date'],
        y=data['min'],
        mode='lines+text',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False,
        text=[f'-{name}' for name in round((data['mean_no'] - data['min']), 1)],
        textposition="bottom center",
        textfont=dict(
            family="sans serif",
            size=10,
            color="#2CA02C",
        )
    ))

    fig.add_trace(go.Scatter(
        name='Отклонение вверх',
        x=data['date'],
        y=data['max'],
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines+text',
        fillcolor='rgba(213, 113, 7, 0.3)',
        fill='tonexty',
        showlegend=False,
        text=[f'+{name}' for name in round((data['max'] - data['mean_no']), 1)],
        textposition="top center",
        textfont=dict(
            family="sans serif",
            size=10,
            color="#EF553B"
        )

    ))

    fig.update_yaxes(
        title_text="Процент",
        title_standoff=15,
        rangemode="tozero")

    fig.update_xaxes(
        title_text="Дата",
        title_standoff=15,
        tickformat='%d.%m.%y')

    fig.update_layout(title_text=f"Проценты отсутствующих товаров в Elasticsearch<br>(случайная выборка из брендов) ",
                      title_x=0.5,
                      showlegend=False,
                      template="simple_white")

    # fig.show()

    return fig


def generate_plot(index_name):

    """
    Функция для генерации карточки с графиком динамики изменения количества записей в индексе

    Args:
        index_name(str): название индекса

    Returns:
        dbc.Card: карточка с графиком.
    """

    card = dbc.Card(
        dcc.Graph(id=f'{index_name}_line', figure=plot_line(index_history, index_name),
                  config={'displayModeBar': False}),
        style={'padding-left': '0px', 'box-shadow': 'none'})
    return card


# первая карточка - количество записей в индексе wb_items
wb_items = generate_card('wb_items')

# добавляем график
wb_items_graph = generate_plot('wb_items')

# добавляем график не обновленных
wb_items_not_upd = dbc.Card(
    dcc.Graph(id='not_upd', figure=plot_all_data(df_not_upd), config={'displayModeBar': False}),
    style={'padding-left': '0px', 'box-shadow': 'none'})

# добавляем график для брендов
wb_items_random_brands = dbc.Card(
    dcc.Graph(id='rand_brand', figure=plot_random_brands(df_random_brands), config={'displayModeBar': False}),
    style={'padding-left': '0px', 'box-shadow': 'none'})

# вторая карточка - количество записей в индексе wb_brands
wb_brands = generate_card('wb_brands')

# добавляем график
wb_brands_graph = generate_plot('wb_brands')

# категории
wb_categories = generate_card('wb_categories')

# добавляем график
wb_categories_graph = generate_plot('wb_categories')

# бренды в категориях
wb_brands_in_categories = generate_card('wb_brands_in_categories')

# добавляем график
wb_brands_in_categories_graph = generate_plot('wb_brands_in_categories')

# категории в брендах
wb_categories_in_brands = generate_card('wb_categories_in_brands')

# добавляем график
wb_categories_in_brands_graph = generate_plot('wb_categories_in_brands')

# зададим общий стиль для всех строк
width = {"size": 2}
style = {"padding-bottom": "10px", "padding-left": "10px", "padding-top": "70px"}
style_graph = {"padding-bottom": "10px", "padding-left": "40px", "padding-top": "20px"}

app_dash.layout = html.Div([
    dbc.Row(dbc.Col([html.H2(f"Динамика изменения количества уникальных записей в индексах Elasticsearch",
                             style={'text-align': 'center',
                                    'text-transform': 'uppercase',
                                    'padding-bottom': "30px",
                                    'padding-top': "30px"
                                    })])),
    dbc.Row([
        dbc.Col(wb_items, width=width, style=style),
        dbc.Col(wb_items_graph, width=4,
                style=style_graph),
        dbc.Col(wb_items_random_brands, width={"size": 6}, style=style_graph),
    ], no_gutters=True),
    dbc.Row([dbc.Col(wb_items_not_upd, width={"size": 10, "offset": 1},
                style=style_graph)

    ], no_gutters=True),
    dbc.Row([
        dbc.Col(wb_brands, width=width, style=style),
        dbc.Col(wb_brands_graph, width=10,
                style=style_graph),
    ], no_gutters=True),
    dbc.Row([
        dbc.Col(wb_categories, width=width, style=style),
        dbc.Col(wb_categories_graph, width=10,
                style=style_graph),
    ], no_gutters=True),
    dbc.Row([
        dbc.Col(wb_brands_in_categories, width=width, style=style),
        dbc.Col(wb_brands_in_categories_graph, width=10,
                style=style_graph),
    ], no_gutters=True),
    dbc.Row([
        dbc.Col(wb_categories_in_brands, width=width, style=style),
        dbc.Col(wb_categories_in_brands_graph, width=10,
                style=style_graph),
    ], no_gutters=True),
])

if __name__ == '__main__':
    app_dash.run_server(debug=True)
