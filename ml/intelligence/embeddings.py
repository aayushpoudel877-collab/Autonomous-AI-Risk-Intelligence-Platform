from abc import ABC,abstractmethod
import numpy as np

class EmbeddingProvider(ABC):
    @abstractmethod
    def encode(self,texts): ...

class HashEmbeddingProvider(EmbeddingProvider):
    def __init__(self,dimensions=128):
        self.dimensions=dimensions
    def encode(self,texts):
        vectors=[]
        for text in texts:
            v=np.zeros(self.dimensions,dtype=float)
            for token in text.lower().split():
                v[hash(token)%self.dimensions]+=1.0
            norm=np.linalg.norm(v)
            vectors.append(v/norm if norm else v)
        return np.asarray(vectors)

class RetrievalIndex:
    def __init__(self,provider=None):
        self.provider=provider or HashEmbeddingProvider()
        self.chunks=[]
        self.vectors=np.empty((0,self.provider.dimensions))
    def add(self,chunks):
        if not chunks:return
        self.chunks.extend(chunks)
        encoded=self.provider.encode([c.text for c in chunks])
        self.vectors=np.vstack([self.vectors,encoded])
    def search(self,query,top_k=5):
        if not self.chunks:return []
        q=self.provider.encode([query])[0]
        scores=self.vectors@q
        order=np.argsort(-scores)[:top_k]
        return [(self.chunks[i],float(scores[i])) for i in order if scores[i]>0]
