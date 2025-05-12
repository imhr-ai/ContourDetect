import cv2
import numpy as np
import os
import glob

# --- 設定項目 ---
# ご自身の環境に合わせて変更してください
IMAGE_DIR = 'your_image_directory'  # 画像が保存されているディレクトリパス
OUTPUT_DIR = 'output_mask_directory' # マスク結果を保存するディレクトリパス

# リサイズ後の画像の幅 (高さはアスペクト比を維持して自動計算)
RESIZE_WIDTH = 800

# マスクで塗りつぶす色 (BGR形式)
MASK_COLOR = (0, 0, 0)  # 黒色で塗りつぶす場合

# --- 設定項目ここまで ---

def create_and_apply_donut_masks(image_path, output_base_dir, resize_width):
    """
    一枚の画像に対してドーナツ型の内側と外側をマスクする処理を行います。
    """
    try:
        # 1. 画像の読み込み
        img = cv2.imread(image_path)
        if img is None:
            print(f"画像の読み込みに失敗しました: {image_path}")
            return

        # 1a. リサイズ
        original_height, original_width = img.shape[:2]
        aspect_ratio = original_height / original_width
        resized_height = int(resize_width * aspect_ratio)
        resized_img = cv2.resize(img, (resize_width, resized_height), interpolation=cv2.INTER_AREA)
        h, w = resized_img.shape[:2]

        # 2. 前処理
        gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
        # ガウシアンブラーで平滑化 (カーネルサイズは画像のノイズに応じて調整)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # 3. 二値化
        # 適応的閾値処理 (blockSizeとCの値は画像の特性に合わせて調整してください)
        # THRESH_BINARY_INV: 物体を白、背景を黒にする
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                       cv2.THRESH_BINARY_INV, blockSize=15, C=5) # blockSizeは奇数

        # モルフォロジー演算でノイズ除去や穴埋め (必要に応じて調整)
        kernel = np.ones((5,5),np.uint8)
        thresh_cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        thresh_cleaned = cv2.morphologyEx(thresh_cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 4. 輪郭抽出
        # cv2.RETR_CCOMP: 全ての輪郭を抽出し、2レベルの階層構造を構成（外側輪郭と内側輪郭のペアを見つけやすい）
        contours, hierarchy = cv2.findContours(thresh_cleaned, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        if hierarchy is None or len(hierarchy) == 0:
            print(f"輪郭が見つかりませんでした: {image_path}")
            # デバッグ用に二値化画像を保存
            debug_thresh_path = os.path.join(output_base_dir, "debug_thresh")
            os.makedirs(debug_thresh_path, exist_ok=True)
            cv2.imwrite(os.path.join(debug_thresh_path, f"{os.path.splitext(os.path.basename(image_path))[0]}_thresh.png"), thresh_cleaned)
            return

        # ドーナツの輪郭ペア (外側輪郭, 内側輪郭) を探す
        donut_contours_pairs = []
        # hierarchy[0][i] = [Next, Previous, First_Child, Parent]
        for i in range(len(contours)):
            # i 番目の輪郭が外側の輪郭である候補 (親がいない or 親も外側の輪郭)
            # かつ、子を持つ (つまり穴がある)
            if hierarchy[0][i][2] != -1 and (hierarchy[0][i][3] == -1 or hierarchy[0][hierarchy[0][i][3]][3] == -1) :
                outer_contour_candidate = contours[i]
                # その最初の子を内側輪郭候補とする
                inner_contour_idx = hierarchy[0][i][2]
                inner_contour_candidate = contours[inner_contour_idx]

                # 内側の輪郭候補がさらに子を持たないことを確認（単純な穴の場合）
                if hierarchy[0][inner_contour_idx][2] == -1:
                    area_outer = cv2.contourArea(outer_contour_candidate)
                    area_inner = cv2.contourArea(inner_contour_candidate)
                    # 面積である程度フィルタリング（外側が内側より大きく、内側もある程度の面積を持つ）
                    # この閾値は画像の内容によって調整が必要
                    if area_outer > area_inner and area_inner > (w * h * 0.001): # 内側の穴が画像の0.1%以上など
                        donut_contours_pairs.append((outer_contour_candidate, inner_contour_candidate))

        if not donut_contours_pairs:
            print(f"ドーナツ形状の輪郭ペアが見つかりませんでした: {image_path}")
            # デバッグ用に輪郭描画画像を保存
            debug_contour_path = os.path.join(output_base_dir, "debug_contours")
            os.makedirs(debug_contour_path, exist_ok=True)
            img_with_contours = resized_img.copy()
            cv2.drawContours(img_with_contours, contours, -1, (0,255,0), 2)
            cv2.imwrite(os.path.join(debug_contour_path, f"{os.path.splitext(os.path.basename(image_path))[0]}_contours.png"), img_with_contours)
            return

        # 複数のドーナツが見つかった場合、最大の面積を持つものを選択
        donut_contours_pairs.sort(key=lambda pair: cv2.contourArea(pair[0]), reverse=True)
        selected_outer_contour, selected_inner_contour = donut_contours_pairs[0]

        # 5. マスク作成
        # 内側マスク (ドーナツの穴の部分)
        mask_inner = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(mask_inner, [selected_inner_contour], -1, 255, thickness=cv2.FILLED)

        # 外側マスク (画像全体 - ドーナツの外側の輪郭の内側)
        mask_outer = np.full((h, w), 255, dtype=np.uint8) # 画像全体を白(255)で初期化
        cv2.drawContours(mask_outer, [selected_outer_contour], -1, 0, thickness=cv2.FILLED) # 外側輪郭の内側を黒(0)で塗りつぶす

        # ドーナツ本体のマスク (外側輪郭の内側 - 内側輪郭の内側)
        mask_donut_body = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(mask_donut_body, [selected_outer_contour], -1, 255, thickness=cv2.FILLED)
        cv2.drawContours(mask_donut_body, [selected_inner_contour], -1, 0, thickness=cv2.FILLED)


        # 6. 結果の保存
        base_filename = os.path.splitext(os.path.basename(image_path))[0]

        # モノクロマスク画像の保存先ディレクトリ
        output_mono_masks_dir = os.path.join(output_base_dir, "monochrome_masks")
        os.makedirs(output_mono_masks_dir, exist_ok=True)
        cv2.imwrite(os.path.join(output_mono_masks_dir, f"{base_filename}_mask_inner_monochrome.png"), mask_inner)
        cv2.imwrite(os.path.join(output_mono_masks_dir, f"{base_filename}_mask_outer_monochrome.png"), mask_outer)
        cv2.imwrite(os.path.join(output_mono_masks_dir, f"{base_filename}_mask_donut_body_monochrome.png"), mask_donut_body)

        # マスク適用画像の保存先ディレクトリ
        output_masked_images_dir = os.path.join(output_base_dir, "masked_images")
        os.makedirs(output_masked_images_dir, exist_ok=True)

        # 内側をマスクした画像 (ドーナツの穴を指定色で塗りつぶし)
        img_masked_inner_area = resized_img.copy()
        img_masked_inner_area[mask_inner == 255] = MASK_COLOR
        cv2.imwrite(os.path.join(output_masked_images_dir, f"{base_filename}_masked_inner_area.png"), img_masked_inner_area)

        # 外側をマスクした画像 (ドーナツの外側背景を指定色で塗りつぶし)
        img_masked_outer_area = resized_img.copy()
        img_masked_outer_area[mask_outer == 255] = MASK_COLOR
        cv2.imwrite(os.path.join(output_masked_images_dir, f"{base_filename}_masked_outer_area.png"), img_masked_outer_area)

        # ドーナツ本体のみの画像 (内側と外側の両方をマスク)
        img_donut_only = resized_img.copy()
        # ドーナツ本体以外の領域を示すマスク (内側マスクと外側マスクのOR)
        mask_not_donut_body = cv2.bitwise_or(mask_inner, mask_outer)
        img_donut_only[mask_not_donut_body == 255] = MASK_COLOR
        # もしくは、ドーナツ本体のマスクを使ってAND演算でも可
        # img_donut_only = cv2.bitwise_and(resized_img, resized_img, mask=mask_donut_body)
        # img_donut_only[mask_donut_body == 0] = MASK_COLOR # ドーナツ以外の部分を塗りつぶし
        cv2.imwrite(os.path.join(output_masked_images_dir, f"{base_filename}_donut_only.png"), img_donut_only)

        print(f"処理完了: {image_path}")

    except Exception as e:
        print(f"エラー発生 ({image_path}): {e}")


def main():
    # 出力ディレクトリ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # デバッグ用ディレクトリも作成
    os.makedirs(os.path.join(OUTPUT_DIR, "debug_thresh"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "debug_contours"), exist_ok=True)


    # 画像ファイルのリストを取得 (一般的な画像フォーマットに対応)
    image_extensions = ('*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.gif')
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(IMAGE_DIR, ext)))
    
    if not image_files:
        print(f"指定されたディレクトリに画像が見つかりません: {IMAGE_DIR}")
        print("IMAGE_DIRのパスが正しいか、ディレクトリ内に画像ファイルがあるか確認してください。")
        return

    print(f"{len(image_files)} 件の画像を処理します...")

    for image_file_path in image_files:
        create_and_apply_donut_masks(image_file_path, OUTPUT_DIR, RESIZE_WIDTH)

    print("-" * 30)
    print("全ての処理が完了しました。")
    print(f"結果は {OUTPUT_DIR} に保存されています。")
    print(f"内側をマスクした画像: {os.path.join(OUTPUT_DIR, 'masked_images', 'FILENAME_masked_inner_area.png')}")
    print(f"外側をマスクした画像: {os.path.join(OUTPUT_DIR, 'masked_images', 'FILENAME_masked_outer_area.png')}")
    print(f"ドーナツ本体のみの画像: {os.path.join(OUTPUT_DIR, 'masked_images', 'FILENAME_donut_only.png')}")
    print(f"モノクロマスク画像: {os.path.join(OUTPUT_DIR, 'monochrome_masks')}")


if __name__ == '__main__':
    # --- 実行前にお読みください ---
    # 1. スクリプト上部の `IMAGE_DIR` 変数に、処理したい画像が含まれるフォルダのパスを指定してください。
    #    例: IMAGE_DIR = '/path/to/your/donut_images'
    # 2. スクリプト上部の `OUTPUT_DIR` 変数に、処理結果を保存したいフォルダのパスを指定してください。
    #    このフォルダはスクリプト実行時に自動的に作成されます（存在しない場合）。
    #    例: OUTPUT_DIR = '/path/to/your/output_folder'
    # 3. `RESIZE_WIDTH` や `MASK_COLOR` も必要に応じて調整してください。
    # 4. 画像の特性によっては、`cv2.GaussianBlur`のカーネルサイズ、`cv2.adaptiveThreshold`の`blockSize`や`C`の値、
    #    モルフォロジー演算のカーネルサイズや繰り返し回数の調整が必要になる場合があります。
    #    これらはコメントで `調整してください` と記載のある箇所です。
    #
    # --- 準備ができたら、このスクリプトを実行してください ---

    # 以下の行のコメントを解除し、実際のパスを設定してください
    # IMAGE_DIR = 'C:/Users/YourUser/Desktop/DonutImages'  # Windowsの例
    # OUTPUT_DIR = 'C:/Users/YourUser/Desktop/DonutOutput' # Windowsの例

    if IMAGE_DIR == 'your_image_directory' or OUTPUT_DIR == 'output_mask_directory':
        print("スクリプトの先頭にある IMAGE_DIR と OUTPUT_DIR を実際のパスに設定してください。")
    else:
        main()
