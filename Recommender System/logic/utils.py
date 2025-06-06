import numpy as np
import nltk
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize  
from gensim.utils import simple_preprocess 
from nltk.corpus import stopwords
nltk.download("stopwords")
stop_words = stopwords.words("english")

## Text Preprocessing 

# 1. str.lower()

def lower_text(text):
    text = text.lower()
    return text


### 2. Remove punctuations

def remove_punct(string):
    for i in string:

        puncts = '''!()-[]{};:'",<>./?@#$%^&*_~'''
        if i in puncts:
           string = string.replace(i,'')

    return string


## 3 Tokenize

def tokenize(text):
    tokens = word_tokenize(text)
    return tokens



# 4. Remove stopwords


from nltk.corpus import stopwords
stopwords = stopwords.words('english')


def remove_stopwords(text):
    for i in text:
        if i in stopwords:
            text.remove(i)
    return text


def preprocess(text):
    tokens = simple_preprocess(text,deacc= True)
    return [word for word in tokens if word not in stop_words]


def tokens_to_vec(token_text, model,vector_size=100):
    # Filter tokens in the model's vocabulary
    valid_tokens = [token for token in token_text if token in model.wv]
    
    # Handle empty valid_tokens gracefully
    if not valid_tokens:
        return np.zeros((1, vector_size))  # Return zero vector if no valid tokens
    
    # Get embeddings for valid tokens
    token_embeddings = model.wv[valid_tokens]
    
    # Compute mean embedding
    mean_embedding = np.mean(token_embeddings, axis=0)

    return mean_embedding
    
