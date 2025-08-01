option = {
  // gridの左側に余白を持たせ、カテゴリ名や補助線が描画されるスペースを確保します
  grid: {
    left: '10%' // 必要に応じて調整してください
  },
  xAxis: {
    type: 'value'
  },
  yAxis: {
    type: 'category',
    data: ['カテゴリA', 'カテゴリB', 'カテゴリC', 'カテゴリD', 'カテゴリE'],
    // --- ここからが補助線の設定 ---
    axisTick: {
      show: true,           // 目盛りを表示する
      alignWithLabel: true, // ラベルの位置に目盛りを合わせる
      length: 10,             // 目盛りの長さを設定（この長さを調整して補助線に見せる）
      lineStyle: {
        color: '#888',      // 線の色
        width: 1            // 線の太さ
      }
    }
    // --- ここまで ---
  },
  series: [{
    data: [120, 200, 150, 80, 70],
    type: 'bar'
  }]
};