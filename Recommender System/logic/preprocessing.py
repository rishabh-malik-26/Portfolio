from gensim.models import Word2Vec
from utils import *
from qdrant import *



# title1 = "Hair Brush for Women"

def get_similar_titles(title,limit):
    model = Word2Vec.load(r"C:\Users\Rishabh\Desktop\Python New\Amazon Recommender System\word2vec_model.model")
    procesed_text = preprocess(title)
    title_tokens = tokens_to_vec(procesed_text,model=model)
    client = Qdrant()
    similar_titles = client.search("test_collection",query_vector =title_tokens,limit = limit)
    return similar_titles

# print(get_similar_titles(title1))


