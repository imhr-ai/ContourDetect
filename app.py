import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

def get_log_data_for_timeline():
    """
    ログを解析し、Vis.js Timeline用の形式に変換する
    """
    # サンプルデータ（実際のログに合わせて修正してください）
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
    # タイムスタンプをdatetimeオブジェクトに変換
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 1. groupsの作成 (Y軸のスレッドリスト)
    all_threads = pd.concat([df['from_thread'], df['to_thread']]).unique()
    groups = [{'id': thread, 'content': thread} for thread in all_threads]

    # 2. itemsの作成 (タイムライン上のイベント)
    items = []
    for index, row in df.iterrows():
        # 送信元スレッドにイベントを配置
        items.append({
            'id': f"{index}-from",
            'group': row['from_thread'], # Y軸のどのグループに属するか
            'content': f"➡ {row['to_thread']}: {row['message']}", # 表示内容
            'start': row['timestamp'].isoformat(), # X軸の位置
            'type': 'box', # 表示形式
            'title': f"<pre>{row['full_log']}</pre>" # ホバー時に表示されるツールチップ
        })
        # 受信側にも点を打つと分かりやすい (オプション)
        items.append({
            'id': f"{index}-to",
            'group': row['to_thread'],
            'content': f"⬅ {row['from_thread']}",
            'start': row['timestamp'].isoformat(),
            'type': 'point', # 表示形式を点にする
            'title': f"<pre>{row['full_log']}</pre>"
        })


    return groups, items

@app.route('/')
def index():
    return render_template('index.html')

# APIエンドポイント
@app.route('/api/timeline-logs')
def get_timeline_logs():
    groups, items = get_log_data_for_timeline()
    return jsonify({
        'groups': groups,
        'items': items
    })

if __name__ == '__main__':
    app.run(debug=True)