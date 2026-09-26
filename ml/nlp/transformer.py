from dataclasses import dataclass

try:
    from transformers import AutoTokenizer, AutoModel
except ImportError:
    AutoTokenizer = None
    AutoModel = None

@dataclass(frozen=True)
class TextEmbedding:
    vector: list[float]
    model_name: str

class TransformerTextEncoder:
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        if AutoTokenizer is None:
            raise ImportError("Transformers is required. Install aegismind[nlp].")
        self.model_name=model_name
        self.tokenizer=AutoTokenizer.from_pretrained(model_name)
        self.model=AutoModel.from_pretrained(model_name)

    def encode(self, text: str) -> TextEmbedding:
        import torch
        inputs=self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            hidden=self.model(**inputs).last_hidden_state
        pooled=hidden.mean(dim=1).squeeze(0).cpu().numpy().round(6).tolist()
        return TextEmbedding(vector=pooled, model_name=self.model_name)
