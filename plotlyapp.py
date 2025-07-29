import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

def get_raw_log_data():
    """
    ログを解析し、Pythonの辞書のリスト（JSONにしやすい形式）で返す
    """
    # ここで実際のログファイルを読み込み、DataFrameに変換
    # 以下はサンプルデータ
    # 実際には2000件のデータが生成されると想定
    data = {
        'timestamp': pd.to_datetime(['2023-10-27 10:00:01.123', '2023-10-27 10:00:02.456', '2023-10-27 10:00:03.789', '2023-10-27 10:00:05.200']),
        'from_thread': ['ThreadA', 'ThreadB', 'ThreadA', 'ThreadC'],
        'to_thread': ['ThreadB', 'ThreadC', 'ThreadC', 'ThreadA'],
        'message': ['Do something', 'Task received', 'Finalize', 'Acknowledge'],
        'full_log': ['...log A...', '...log B...', '...log C...', '...log D...']
    }
    df = pd.DataFrame(data)
    
    # フロントエンドで扱いやすいように、タイムスタンプをISO形式文字列に変換
    df['timestamp_iso'] = df['timestamp'].apply(lambda x: x.isoformat())
    
    # DataFrameを辞書のリストに変換して返す
    return df.to_dict(orient='records')

@app.route('/')
def index():
    return render_template('index.html')

# APIエンドポイント: 生のログデータをJSONで返す
@app.route('/api/raw-logs')
def get_raw_logs():
    logs = get_raw_log_data()
    return jsonify(logs)