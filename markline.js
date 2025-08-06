series: [{
    type: 'line',
    data: [/* ... */],
    markLine: {
        data: [
            {
                yAxis: 100, // ここが重要！Y軸の値を指定するだけ
                name: '目標ライン',
                lineStyle: {
                    color: 'blue',
                    width: 2
                },
                emphasis: { // ホバー時の強調表示
                    lineStyle: {
                        width: 4,
                        color: 'red'
                    }
                },
                tooltip: { // ホバー時の情報表示
                    formatter: '目標値: {c}'
                }
            }
        ]
    }
}]