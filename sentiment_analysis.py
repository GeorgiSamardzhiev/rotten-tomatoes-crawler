import pandas as pd
import csv
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import precision_score, recall_score, f1_score
from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import re

flatten = lambda t: [item for sublist in t for item in sublist]

def read_data_from_file(dataset_file):
    reviews_df = pd.read_csv(dataset_file,delimiter='\t')
    return reviews_df

save_model = lambda model, name: dump(model, name) 

load_model = lambda name: load(name)

def load_model_by_vectorizer_and_predictor(vectorizer, predictor):
    return load_model(f"model_{vectorizer[0]}_{predictor[0]}.joblib")

def vectorizers_and_predictors():
    tfidf1 = TfidfVectorizer()
    tfidf2 = TfidfVectorizer(ngram_range=(1, 2))
    tfidf3 = TfidfVectorizer(ngram_range=(1, 3))
    cv1 = CountVectorizer()
    cv2 = CountVectorizer(ngram_range=(1, 2))
    cv3 = CountVectorizer(ngram_range=(1, 3))

    svc = LinearSVC(max_iter = 2500)
    sgd =  SGDClassifier(max_iter = 2500)
    logistic_regression = LogisticRegression(n_jobs = -1, max_iter = 2500)
    mnb = MultinomialNB()
    bnb = BernoulliNB()
    decision_tree = DecisionTreeClassifier(max_features=3000)
    random_forest = RandomForestClassifier(max_depth=10, n_jobs = -1, n_estimators=100, max_features=3000)

    vectorizers = [('tdidf1', tfidf1), ('tdidf2', tfidf2), ('tdidf3', tfidf3), ('cv1', cv1), ('cv2', cv2), ('cv3', cv3)]
    predictors = [('sgd', sgd), ('svc', svc), ('logistic_regression', logistic_regression), ('mnb', mnb), ('bnb', bnb), ('decision_tree', decision_tree), ('random_forest', random_forest)]

    return vectorizers, predictors

def train_models(train, test, vectorizers, predictors):
    phrase_ids = test['PhraseId'].tolist()
    for vectorizer in vectorizers:
        for predictor in predictors:
            model = Pipeline([vectorizer, predictor])

            predicted_labels = cross_val_predict(model, train[train.columns[0]], train[train.columns[1]], cv=5)

            recall = round(recall_score(train[train.columns[1]], predicted_labels, average = 'weighted', labels=np.unique(predicted_labels)),2)
            precision = round(precision_score(train[train.columns[1]], predicted_labels, average = 'weighted', labels=np.unique(predicted_labels)),2)
            f1 = round(f1_score(train[train.columns[1]], predicted_labels, average = 'weighted', labels=np.unique(predicted_labels)),2)

            print(f"recall score {vectorizer[0]}_{predictor[0]}: ", recall)
            print(f"precision score {vectorizer[0]}_{predictor[0]}: ", precision)
            print(f"f1 score {vectorizer[0]}_{predictor[0]}: ", f1)
            print("\n")

            model.fit(train[train.columns[0]], train[train.columns[1]])
            save_model(model, f"model_{vectorizer[0]}_{predictor[0]}.joblib")
            predictions = model.predict(test[test.columns[2]])
            with open(f"results_{vectorizer[0]}_{predictor[0]}.csv", 'w') as f:
                writer = csv.writer(f)
                writer.writerow(["PhraseId","Sentiment"])
                writer.writerows(zip(phrase_ids, predictions))

def number_to_word_category(number):
    if (number == 0):
        return 'negative'
    if (number == 1):
        return 'somewhat negative'
    if (number == 2):
        return 'neutral'
    if (number == 3):
        return 'somewhat positive'
    if (number == 4):
        return 'positive'

def preprocess(text):
    ps = PorterStemmer()
    stemmed = []
    for words in text:
        words_split = re.split(r'[;,\s]\s*', words.lower())
        stemmed_words = []
        for word in words_split:
            stemmed_words.append(ps.stem(word))
        stemmed.append(' '.join(stemmed_words))
    return stemmed
