from dataclasses import dataclass

try:
    import torch
    from torchvision.models import resnet18, ResNet18_Weights
except ImportError:
    torch=None
    resnet18=None
    ResNet18_Weights=None

@dataclass(frozen=True)
class VisionEmbedding:
    vector: list[float]
    model_name: str

class ResNetRiskEncoder:
    def __init__(self, pretrained: bool=False):
        if torch is None: raise ImportError("torchvision is required. Install aegismind[vision].")
        weights=ResNet18_Weights.DEFAULT if pretrained else None
        base=resnet18(weights=weights)
        self.model_name="resnet18"
        self.model=torch.nn.Sequential(*list(base.children())[:-1])
        self.model.eval()

    def encode(self, batch_tensor):
        with torch.no_grad():
            vector=self.model(batch_tensor).flatten(1).mean(dim=0).cpu().numpy().round(6).tolist()
        return VisionEmbedding(vector=vector, model_name=self.model_name)
