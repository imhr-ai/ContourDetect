import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

def parse_log_data():
    # サンプルデータを使用します。
    data = {
        'timestamp': ['2023-10-27 10:00:01.123', '2023-10-27 10:00:02.456', '2023-10-27 10:00:03.789'],
        'from_thread': ['ThreadA', 'ThreadB', 'ThreadA'],
        'to_thread': ['ThreadB', 'ThreadC', 'ThreadC'],
        'message': ['Do something', 'Task received', 'Finalize'],
        'full_log': ['DEBUG: ThreadA sent "Do something" to ThreadB', 'INFO: ThreadB got "Task received" from ThreadA', 'DEBUG: ThreadA sent "Finalize" to ThreadC']
    }
    df = pd.DataFrame(data)

    # 1. Mermaid.jsのシーケンス図構文を生成
    sequence_text = "sequenceDiagram\n"
    # actor宣言を追加して、各スレッドにIDを振る
    participants = df['from_thread'].append(df['to_thread']).unique()
    for p in participants:
        sequence_text += f"    participant {p} as {p}\n"

    # 2. 各メッセージにIDを付与し、詳細情報を作成
    details = {}
    for index, row in df.iterrows():
        message_id = f"msg-{index}"
        # メッセージにIDを付与する構文 (Mermaid 9.4+で利用可能)
        sequence_text += f"    link {row['from_thread']}->>{row['to_thread']}: {row['message']}: {message_id}\n"
        
        details[message_id] = {
            'timestamp': row['timestamp'],
            'from': row['from_thread'],
            'to': row['to_thread'],
            'full_log': row['full_log']
        }

    return sequence_text, details

@app.route('/')
def index():
    return render_template('index.html')

# データを返すAPIを修正
@app.route('/api/logs')
def get_log_data():
    sequence_data, details_data = parse_log_data()
    return jsonify({
        'sequence': sequence_data,
        'details': details_data
    })

if __name__ == '__main__':
    app.run(debug=True)