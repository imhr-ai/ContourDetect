import plotly.express as px
import pandas as pd

# サンプルデータ
df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'A': [10, 15, 13, 17, 20],
    'B': [5, 8, 12, 9, 7]
}).melt(id_vars='x', var_name='series', value_name='y')

# 折れ線グラフを作成
fig = px.line(df, x='x', y='y', color='series', title="hovermode='x unified' の例")

# 1. マーカーを非表示にして線だけにする
#    （マーカーは非表示でもホバーの対象としては残ります）
fig.update_traces(mode='lines')

# 2. hovermodeを'x unified'に設定
fig.update_layout(hovermode='x unified')

fig.show()
