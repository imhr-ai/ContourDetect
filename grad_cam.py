class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None

        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach() # 勾配計算に関与しないようにdetach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach() # 勾配計算に関与しないようにdetach()

        self.forward_handle = self.target_layer.register_forward_hook(forward_hook)
        # PyTorch 1.8.0 以降では register_full_backward_hook が推奨されます
        # それ以前のバージョンでは register_backward_hook を使う必要がありますが、
        # grad_output を直接取得できる register_full_backward_hook の方がGrad-CAMには適しています。
        if hasattr(self.target_layer, 'register_full_backward_hook'):
            self.backward_handle = self.target_layer.register_full_backward_hook(backward_hook)
        else: # 古いPyTorchバージョンのためのフォールバック (動作が異なる可能性あり)
            self.backward_handle = self.target_layer.register_backward_hook(backward_hook_legacy)
            # def backward_hook_legacy(module, grad_input, grad_output):
            #     # register_backward_hookの場合、grad_outputはタプルで、その最初の要素が勾配。
            #     # ただし、これが「層の出力に対する勾配」と一致するかはモジュール構造に依存。
            #     # ResNetのSequentialの場合、これが適切に機能するか検証が必要。
            #     # 通常は register_full_backward_hook を使用すべき。
            #     self.gradients = grad_output[0].detach()


    def _get_gradcam_weights(self):
        # グローバルアベレージプーリングで勾配から重みを計算
        # gradients: (batch, channels, height, width)
        # weights: (batch, channels)
        return torch.mean(self.gradients, dim=(2, 3), keepdim=True)

    def generate_heatmap(self, class_idx=None):
        if self.activations is None or self.gradients is None:
            raise RuntimeError("Activations or gradients not found. Ensure forward and backward passes are done.")

        # 1. 勾配から重みを計算 (alpha_k^c)
        weights = self._get_gradcam_weights() # (batch, channels, 1, 1)

        # 2. 活性化マップと重みの加重和
        # activations: (batch, channels, height, width)
        # weighted_activations: (batch, channels, height, width)
        weighted_activations = weights * self.activations
        
        # cam: (batch, 1, height, width)
        cam = torch.sum(weighted_activations, dim=1, keepdim=True)

        # 3. ReLUを適用
        cam = F.relu(cam)
        
        # バッチサイズが1であることを想定して、最初の要素を取り出す
        cam = cam.squeeze(0).squeeze(0) # (height, width)
        return cam.cpu().numpy()

    def __call__(self, input_tensor, class_idx=None):
        self.model.zero_grad()
        
        # フォワードパス (フックにより self.activations が設定される)
        output = self.model(input_tensor) # (batch, num_classes)

        if class_idx is None:
            # 指定がない場合は、予測確率最大のクラスを使用
            class_idx = torch.argmax(output, dim=1).item()
        
        # 目的のクラスのスコア
        target_score = output[:, class_idx]

        # バックワードパス (フックにより self.gradients が設定される)
        target_score.backward(retain_graph=False) # 通常はretain_graph=Falseで良い

        # ヒートマップ生成
        heatmap = self.generate_heatmap()
        
        return heatmap, class_idx

    def remove_hooks(self):
        self.forward_handle.remove()
        self.backward_handle.remove()
        self.activations = None
        self.gradients = None
        
# GradCAMインスタンスの作成
grad_cam = GradCAM(model, target_layer)

# Grad-CAMの計算 (特定のクラスID、または最も確率の高いクラス)
# 例: ImageNetのクラスID 243 (affenpinscher, a Poodle, a pinscher terrier)
# target_class_idx = 243
target_class_idx = None # Noneにすると予測確率最大のクラスが使われる

heatmap_raw, predicted_class_idx = grad_cam(input_tensor, class_idx=target_class_idx)

# フックを解除 (重要)
grad_cam.remove_hooks()

print(f"Input tensor shape: {input_tensor.shape}")
if grad_cam.activations is not None: # remove_hooks 後は None になっているはず
    print(f"Activations shape: {grad_cam.activations.shape}")
if grad_cam.gradients is not None:
    print(f"Gradients shape: {grad_cam.gradients.shape}")
print(f"Raw heatmap shape: {heatmap_raw.shape}")
print(f"Predicted class index: {predicted_class_idx}")

# (オプション) ImageNetクラスラベルの取得 (簡易版)
# !wget -q https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt -O imagenet_classes.txt
# with open("imagenet_classes.txt", "r") as f:
#     imagenet_classes = [s.strip() for s in f.readlines()]
# print(f"Predicted class name: {imagenet_classes[predicted_class_idx]}")


def show_cam_on_image(img_pil, heatmap_np, alpha=0.5):
    # 1. ヒートマップを0-1に正規化
    heatmap_normalized = (heatmap_np - np.min(heatmap_np)) / (np.max(heatmap_np) - np.min(heatmap_np) + 1e-8)

    # 2. 元のPIL画像をNumPy配列に変換 (0-255, RGB)
    img_np = np.array(img_pil)

    # 3. ヒートマップをリサイズし、カラーマップを適用
    #    OpenCVはBGRを期待するので、img_npもBGRに変換
    heatmap_resized = cv2.resize(heatmap_normalized, (img_np.shape[1], img_np.shape[0]))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB) # Matplotlib用にRGBに戻す

    # 4. 重ね合わせ
    #    img_npがRGBであることを確認
    if img_np.shape[2] == 3 and heatmap_colored_rgb.shape[2] == 3: # カラー画像の場合
        superimposed_img = np.uint8(heatmap_colored_rgb * alpha + img_np * (1 - alpha))
    else: # グレースケール画像などの場合
        superimposed_img = np.uint8(heatmap_colored_rgb * alpha + np.stack((img_np,)*3, axis=-1) * (1 - alpha) )


    # 表示
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 3, 1)
    plt.imshow(img_pil)
    plt.title("Original Image")
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.imshow(heatmap_resized, cmap='jet') # カラーマップ適用前のヒートマップ（リサイズ後）
    plt.title("Grad-CAM Heatmap")
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(superimposed_img)
    plt.title("Superimposed Image")
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

    return superimposed_img

# 可視化の実行
superimposed_image = show_cam_on_image(original_img, heatmap_raw)

import torch
import torch.nn as nn

# フック関数
def simple_hook(module, grad_input, grad_output):
    print(f"Hook called for {module_name}!")
    print(f"  grad_output[0].shape: {grad_output[0].shape}")
    if grad_input[0] is not None:
         print(f"  grad_input[0].shape: {grad_input[0].shape}")

# ダミーのlayer4とfc
layer4_dummy = nn.Conv2d(3, 3, 3)
fc_dummy = nn.Linear(3*6*6, 2) # 入力サイズは適当

# layer4_dummy は凍結しないでおく（もし凍結していてもhookは呼ばれるはず）
# for param in layer4_dummy.parameters():
#     param.requires_grad = False

# fc_dummy は学習対象
for param in fc_dummy.parameters():
    param.requires_grad = True

# フックを登録
module_name = "layer4_dummy"
layer4_dummy.register_full_backward_hook(simple_hook)
print("Hook registered on layer4_dummy")

# ダミー入力
dummy_input = torch.randn(1, 3, 8, 8, requires_grad=True)
# フォワード
x = layer4_dummy(dummy_input)
print(f"Output of layer4_dummy requires_grad: {x.requires_grad}")
x = x.view(x.size(0), -1)
output = fc_dummy(x)
print(f"Output of fc_dummy requires_grad: {output.requires_grad}")


# ダミーのターゲットと損失
target = torch.tensor([1])
loss = nn.CrossEntropyLoss()(output, target)
print(f"Loss: {loss.item()}")

# バックワード
loss.backward()
print("loss.backward() called")

# (オプション) fcの勾配確認
# print(f"fc_dummy.weight.grad is not None: {fc_dummy.weight.grad is not None}")




