import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

def get_log_data_as_list():
    """
    ログを解析し、辞書のリストとして返す。
    実際にはここでログファイルを読み込み、DataFrameに変換してください。
    """
    # サンプルデータ
    data = {
        'timestamp': ['2023-10-27 10:00:01.123', '2023-10-27 10:00:02.456', '2023-10-27 10:00:03.789'],
        'from_thread': ['ThreadA', 'ThreadB', 'ThreadA'],
        'to_thread': ['ThreadB', 'ThreadC', 'ThreadC'],
        'message': ['Do something', 'Task received', 'Finalize'],
        'full_log': [
            '2023-10-27 10:00:01.123 DEBUG: ThreadA sent "Do something" to ThreadB. Details: ...',
            '2023-10-27 10:00:02.456 INFO: ThreadB got "Task received" from ThreadA. Status: OK',
            '2023-10-27 10:00:03.789 DEBUG: ThreadA sent "Finalize" to ThreadC. Result: Success'
        ]
    }
    df = pd.DataFrame(data)
    # DataFrameを辞書のリスト形式（JSONにしやすい）に変換して返す
    return df.to_dict(orient='records')

@app.route('/')
def index():
    return render_template('index.html')

# APIエンドポイント: ログデータをJSONで返す
@app.route('/api/logs')
def get_logs():
    log_data = get_log_data_as_list()
    return jsonify(log_data)

if __name__ == '__main__':
    app.run(debug=True)