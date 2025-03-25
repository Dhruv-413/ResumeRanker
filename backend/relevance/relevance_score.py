import torch
from sklearn.metrics.pairwise import cosine_similarity
from backend.utils.bert_model import tokenizer, model

def compute_similarity_bert(cv_text, job_description):
    def get_embedding(text):
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()
    
    cv_embedding = get_embedding(cv_text)
    job_embedding = get_embedding(job_description)
    similarity = cosine_similarity(cv_embedding, job_embedding)[0][0] * 100
    return round(similarity, 2)