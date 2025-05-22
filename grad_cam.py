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

