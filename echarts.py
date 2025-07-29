import pandas as pd
from flask import Flask, jsonify, render_template
import numpy as np # 大規模サンプルデータ生成用

app = Flask(__name__)

def generate_log_data():
    """
    EChartsでの描画に適した形式で、大規模なログデータを生成する
    """
    # --- サンプルデータ生成 (2000件) ---
    # 実際にはここでログファイルを読み込む
    num_records = 2000
    threads = [f"Thread{chr(65+i)}" for i in range(15)]
    
    timestamps = pd.to_datetime(np.sort(np.random.uniform(
        pd.Timestamp('2023-10-27 10:00:00').timestamp(),
        pd.Timestamp('2023-10-27 10:30:00').timestamp(),
        num_records
    )), unit='s')

    from_threads = np.random.choice(threads, num_records)
    to_threads = np.random.choice(threads, num_records)
    
    for i in range(num_records):
        while from_threads[i] == to_threads[i]:
            to_threads[i] = np.random.choice(threads)
            
    df = pd.DataFrame({
        'timestamp': timestamps,
        'from_thread': from_threads,
        'to_thread': to_threads,
        'message': [f"Msg-{i}" for i in range(num_records)],
        'full_log': [f"Full log details for event {i}..." for i in range(num_records)]
    })
    # ------------------------------------

    # Y軸のカテゴリ（スレッド名）を定義
    y_axis_categories = sorted(threads)

    # フロントエンドで直接使えるように、辞書のリストに変換
    logs_as_dict = df.to_dict(orient='records')
    for log in logs_as_dict:
        log['timestamp'] = log['timestamp'].isoformat() # ISO形式の文字列に

    return {
        'logs': logs_as_dict,
        'categories': y_axis_categories
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/logs')
def get_logs_endpoint():
    data = generate_log_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)