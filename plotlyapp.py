import pandas as pd
from flask import Flask, jsonify, render_template
import numpy as np # サンプルデータ生成用

app = Flask(__name__)

def get_log_data_for_plotly():
    """
    ログデータを生成し、Plotlyでの描画に必要な情報をまとめて返す
    """
    # --- サンプルデータ生成 (2000件) ---
    # 実際にはここでログファイルを読み込んでください
    num_records = 2000
    threads = [f"Thread{chr(65+i)}" for i in range(15)] # ThreadA, ThreadB, ...
    
    timestamps = pd.to_datetime(np.sort(np.random.uniform(
        pd.Timestamp('2023-10-27 10:00:00').timestamp(),
        pd.Timestamp('2023-10-27 11:00:00').timestamp(),
        num_records
    )), unit='s')

    from_threads = np.random.choice(threads, num_records)
    to_threads = np.random.choice(threads, num_records)
    
    # fromとtoが同じにならないようにする
    for i in range(num_records):
        while from_threads[i] == to_threads[i]:
            to_threads[i] = np.random.choice(threads)
            
    data = {
        'timestamp': timestamps,
        'from_thread': from_threads,
        'to_thread': to_threads,
        'message': [f"Message-{i}" for i in range(num_records)],
        'full_log': [f"Full log details for event {i}..." for i in range(num_records)]
    }
    df = pd.DataFrame(data)
    # ------------------------------------

    # Y軸の並び順を固定するため、全スレッドのリストを作成
    all_threads_sorted = sorted(threads, reverse=True)

    # フロントエンドで直接使えるように、辞書のリストに変換
    logs_as_dict = df.to_dict(orient='records')
    
    # タイムスタンプをPlotlyが解釈できるISO形式の文字列に変換
    for log in logs_as_dict:
        log['timestamp'] = log['timestamp'].isoformat()

    # ログデータと、Y軸のカテゴリ情報を両方返す
    return {
        'logs': logs_as_dict,
        'y_axis_categories': all_threads_sorted
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/logs')
def get_logs_endpoint():
    data = get_log_data_for_plotly()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)