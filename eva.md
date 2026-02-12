---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  /* Google Fontsから極太明朝体を読み込み */
  @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@700;900&display=swap');

  /* 全体の基本設定 */
  section {
    font-family: 'Noto Serif JP', serif;
    background-color: #000000;
    color: #ffffff;
    font-weight: 900; /* 極太にする */
    justify-content: center;
  }

  /* 見出し（H1）: エヴァのサブタイトルのような極太・長体 */
  h1 {
    font-size: 80px;
    letter-spacing: -0.05em; /* 文字間を詰める */
    transform: scale(1, 1.3); /* 縦に伸ばしてマティスEBっぽくする */
    margin: 0;
    padding: 20px 0;
    border-bottom: none;
  }

  /* 通常テキスト */
  p, li {
    font-size: 30px;
    font-weight: 700;
    line-height: 1.5;
  }

  /* 強調（赤文字） */
  strong {
    color: #e60012; /* エヴァレッド */
    font-weight: 900;
  }

  /* --- 専用クラス --- */

  /* タイトル画面用：L字型の枠線と大きな文字 */
  section.title {
    display: grid;
    place-items: center;
    align-content: center;
    text-align: center;
  }
  
  /* エヴァ風のサブタイトル装飾（L字枠） */
  .eva-border {
    border-left: 15px solid #fff;
    border-bottom: 15px solid #fff;
    padding: 20px 50px;
    text-align: left;
    display: inline-block;
  }

  /* 縦書きモード（日本のアニメタイトル風） */
  section.vertical {
    writing-mode: vertical-rl;
    text-orientation: upright;
    align-items: center;
  }
  
  /* 緊急事態（EMERGENCY）風 */
  section.emergency {
    background: repeating-linear-gradient(
      45deg,
      #000,
      #000 20px,
      #b00 20px,
      #b00 40px
    );
    color: #fff;
    text-shadow: 2px 2px 0 #000;
  }
  .emergency-box {
    background-color: #e60012;
    color: black;
    border: 5px solid white;
    padding: 20px 60px;
    transform: skewX(-15deg); /* 斜めにする */
    font-family: sans-serif; /* 警告系はゴシックが良い場合も */
    font-weight: 900;
  }

---

<!-- 1枚目：次回予告風タイトル -->

<!-- _class: title -->

<div class="eva-border">
  <h1>第壱話</h1>
  <h1>使徒、襲来</h1>
</div>

---

<!-- 2枚目：縦書きタイトル -->

<!-- _class: vertical -->

# 時に、<br>西暦2024年

---

<!-- 3枚目：通常の箇条書き -->

# 人類補完計画の概要

- **ゼーレ**のシナリオに基づく遂行
- 予算承認の**最終期限**
- 汎用ヒト型決戦兵器の運用
- 第3新東京市の防衛

全ての責任は**碇司令**にある。

---

<!-- 4枚目：EMERGENCY風 -->

<!-- _class: emergency -->

<div class="emergency-box">
  <h1>EMERGENCY</h1>
  <p>パターン青、使徒です！</p>
</div>