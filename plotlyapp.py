import pandas as pd
import plotly.graph_objects as go
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def create_timeline_sequence_chart():
    """
    ログデータを元に、Plotlyでタイムライン型シーケンス図を作成する
    """
    # --- 1. データの準備 (サンプル) ---
    # 実際にはここでログファイルを読み込む
    data = {
        'timestamp': [
            '2023-10-27 10:00:01.123', '2023-10-27 10:00:02.456',
            '2023-10-27 10:00:03.789', '2023-10-27 10:00:05.200'
        ],
        'from_thread': ['ThreadA', 'ThreadB', 'ThreadA', 'ThreadC'],
        'to_thread': ['ThreadB', 'ThreadC', 'ThreadC', 'ThreadA'],
        'message': ['Do something', 'Task received', 'Finalize', 'Acknowledge'],
        'full_log': [
            'DEBUG: ThreadA sent "Do something" to ThreadB.',
            'INFO: ThreadB got "Task received" from ThreadA.',
            'DEBUG: ThreadA sent "Finalize" to ThreadC.',
            'INFO: ThreadC confirmed "Acknowledge" to ThreadA.'
        ]
    }
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Y軸の並び順のため、スレッド名をカテゴリとして定義
    all_threads = sorted(pd.concat([df['from_thread'], df['to_thread']]).unique(), reverse=True)
    df['from_thread'] = pd.Categorical(df['from_thread'], categories=all_threads, ordered=True)
    df['to_thread'] = pd.Categorical(df['to_thread'], categories=all_threads, ordered=True)

    # --- 2. Plotlyグラフの初期化 ---
    fig = go.Figure()

    # --- 3. 各ログを点としてプロット ---
    # これにより、Y軸にスレッド名が表示され、ホバーで情報が見えるようになる
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['from_thread'],
        mode='markers',
        marker=dict(color='blue', size=10, symbol='circle'),
        name='送信元',
        text=[f"To: {to}<br>{msg}" for to, msg in zip(df['to_thread'], df['full_log'])], # ホバーテキスト
        hoverinfo='text'
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['to_thread'],
        mode='markers',
        marker=dict(color='red', size=10, symbol='x'),
        name='受信先',
        text=[f"From: {frm}<br>{msg}" for frm, msg in zip(df['from_thread'], df['full_log'])],
        hoverinfo='text'
    ))


    # --- 4. 送信元から受信先へ矢印を追加 ---
    for index, row in df.iterrows():
        fig.add_annotation(
            ax=row['timestamp'], ay=row['from_thread'], # 矢印の始点 (x, y)
            x=row['timestamp'], xshift=10, # xは同じで少しだけずらす
            y=row['to_thread'], # 矢印の終点 (y)
            showarrow=True,
            arrowhead=2,
            arrowcolor="#636EFA",
            arrowwidth=1.5,
            text=row['message'], # 矢印の横に表示するテキスト
            font=dict(size=10, color="black"),
            align="center"
        )

    # --- 5. レイアウトの調整 ---
    fig.update_layout(
        title='装置ログ タイムラインシーケンス',
        xaxis_title='時間',
        yaxis_title='スレッド',
        yaxis=dict(categoryorder='array', categoryarray=all_threads), # Y軸の並び順を固定
        showlegend=True # 凡例を表示
    )

    # グラフオブジェクトをJSON形式に変換
    return fig.to_json()

@app.route('/')
def index():
    return render_template('index.html')

# APIエンドポイント
@app.route('/api/plotly-chart')
def get_plotly_chart():
    chart_json = create_timeline_sequence_chart()
    return chart_json

if __name__ == '__main__':
    app.run(debug=True)