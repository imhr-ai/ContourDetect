import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor

# GPUが使えるか確認
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

# モデルID
MODEL_ID = "PaddlePaddle/PaddleOCR-VL"

def run_paddleocr_vl(image_path, task="ocr"):
    """
    タスクの種類:
    - 'ocr': 文字認識
    - 'table': 表認識
    - 'formula': 数式認識
    - 'chart': グラフ・チャート認識
    """
    
    print(f"Loading model: {MODEL_ID}...")
    
    # 1. プロセッサの読み込み (画像とテキストの前処理用)
    processor = AutoProcessor.from_pretrained(
        MODEL_ID, 
        trust_remote_code=True
    )
    
    # 2. モデルの読み込み
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        torch_dtype=dtype,
        low_cpu_mem_usage=True
    ).to(DEVICE).eval()

    # タスクごとのプロンプト定義
    prompts = {
        "ocr": "OCR:",
        "table": "Table Recognition:",
        "formula": "Formula Recognition:",
        "chart": "Chart Recognition:",
    }
    
    prompt_text = prompts.get(task, "OCR:")
    
    # 画像を開く
    image = Image.open(image_path).convert("RGB")
    
    # 3. 入力データの作成
    # このモデルはテキストプロンプトと一緒に画像を入力します
    inputs = processor(
        text=prompt_text,
        images=image,
        return_tensors="pt"
    ).to(DEVICE)
    
    # dtypeをモデルに合わせる（processorがfloat32を返すことがあるため）
    if torch.cuda.is_available():
        inputs["pixel_values"] = inputs["pixel_values"].to(dtype)

    print("Generating...")
    
    # 4. 生成実行
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=1024,  # 出力の長さに応じて調整してください
            do_sample=False,      # 決定論的な出力にする場合
            # num_beams=5         # 精度を上げたい場合はビームサーチを有効化
        )

    # 5. 結果のデコード
    # 入力プロンプト部分を除去して出力だけを取り出す処理が含まれる場合があります
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # プロンプト自体が出力に含まれている場合、除去する処理を入れると見やすくなります
    if generated_text.startswith(prompt_text):
        generated_text = generated_text[len(prompt_text):].strip()

    return generated_text

# ==========================================
# 実行例
# ==========================================
if __name__ == "__main__":
    # テストする画像のパス
    img_path = "test_image.png" 
    
    # タスクを選択: 'ocr', 'table', 'formula', 'chart'
    result = run_paddleocr_vl(img_path, task="ocr")
    
    print("-" * 30)
    print("Result:")
    print(result)
    print("-" * 30)