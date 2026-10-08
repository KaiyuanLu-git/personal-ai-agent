from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import jieba

def load_and_chunk(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        s = f.read()
        chunks = s.split("\n\n")
        chunks = [chunk.strip() for chunk in chunks]
    return(chunks)

def tokenize_cn(chunk):
    return " ".join(jieba.cut(chunk))

def vectorize(chunks):
    chunks = [tokenize_cn(chunk) for chunk in chunks]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunks)
    return tfidf_matrix, vectorizer

class KnowledgeBase:
    def __init__(self, filepath):
        self.chunks = load_and_chunk(filepath)
        self.tfidf_matrix, self.vectorizer = vectorize(self.chunks)
    def search(self, query, top_k=3):
            query_tokened = tokenize_cn(query)
            query_vec = self.vectorizer.transform([query_tokened])
            sims = []
            for i in range(len(self.chunks)):
                cos_sim = cosine_similarity(self.tfidf_matrix[i], query_vec)[0][0]
                sims.append(cos_sim)
            id_res = np.argsort(sims)[::-1][:top_k]
            return [self.chunks[i] for i in id_res]
    
kb = KnowledgeBase("doc/doc1.txt")

def knowledge_search(query):
     res = kb.search(query)
     return "搜索结果：" + ";".join(res)



