import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html, Input, Output

# 1. サンプルデータの準備
# 果物ごとの売上データを持つDataFrameを作成します。
df = pd.DataFrame({
    "Fruit": ["りんご", "みかん", "バナナ", "ぶどう", "いちご", "メロン"],
    "Amount": [400, 150, 250, 200, 500, 300],
    "City": ["東京", "大阪", "東京", "大阪", "東京", "大阪"]
})

# 2. Dashアプリケーションの初期化
app = Dash(__name__)

# 3. アプリケーションのレイアウトを定義
app.layout = html.Div([
    html.H1("Y軸の順序をインタラクティブに変更するダッシュボード", style={'textAlign': 'center'}),
    html.Hr(),

    # 並び順を選択するためのラジオボタン
    html.Div([
        html.Label("Y軸の並び順を選択:", style={'fontWeight': 'bold'}),
        dcc.RadioItems(
            id='yaxis-sort-order-radio',
            options=[
                {'label': 'デフォルト', 'value': 'trace'},
                {'label': '合計値の昇順', 'value': 'total ascending'},
                {'label': '合計値の降順', 'value': 'total descending'},
                {'label': 'カテゴリ名の昇順', 'value': 'category ascending'},
                {'label': 'カテゴリ名の降順', 'value': 'category descending'},
            ],
            value='trace', # 初期値
            labelStyle={'display': 'inline-block', 'margin-left': '15px'}
        )
    ], style={'padding': '20px'}),

    # グラフを表示するコンポーネント
    dcc.Graph(id='interactive-bar-chart')
])

# 4. コールバックを定義
# ラジオボタンの選択に応じてグラフを更新します。
@app.callback(
    Output('interactive-bar-chart', 'figure'),
    Input('yaxis-sort-order-radio', 'value')
)
def update_graph(sort_order_value):
    """
    選択された並び順に基づいて棒グラフを更新する関数
    """
    # Plotly Expressで基本的な棒グラフを作成
    fig = px.bar(
        df,
        x="Amount",
        y="Fruit",
        orientation='h', # 横向きの棒グラフ
        title="果物別の売上"
    )

    # 選択された値に応じて、y軸のカテゴリの並び順を更新
    fig.update_layout(
        yaxis={'categoryorder': sort_order_value},
        transition_duration=300 # アニメーション効果
    )

    return fig


# 5. アプリケーションの実行
if __name__ == '__main__':
    app.run_server(debug=True)

