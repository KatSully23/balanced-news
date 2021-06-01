import joblib
from statistics import mean
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import pandas as pd
import re

model = joblib.load('vote_model.joblib')

def clean(text):

    text = re.sub('[\n\t,]', ' ', text)
    text = text.replace('Advertisement', ' ')

    article = []
    article.append(text)
    articles = pd.Series(article)

    stemmer = SnowballStemmer('english')
    words = stopwords.words("english")

    cleaned = articles.apply(lambda x: " ".join([stemmer.stem(i) for i in re.sub("[^a-zA-Z]", " ", x).split() if i not in words]).lower())

    return cleaned



def sentiment(text):
    X = clean(text)
    conf_score = model.transform(X)[0]
    scores = []
    all_classes = []
    for i in range(int(len(conf_score)/2)):
        all_classes.append(conf_score[2*i+1])
    score = mean(all_classes)*4-2
    if score < -0.5:
        if score > -0.75:
            scores = ['left', 0]
        elif score > -1.1:
            scores = ['left', 0.5]
        else:
            scores = ['left', 1]
    else:
        if score < 0.3:
            scores = ['right', 0]
        elif score < 1.1:
            scores = ['right', 0.5]
        else:
            scores = ['right', 1]
    return scores
