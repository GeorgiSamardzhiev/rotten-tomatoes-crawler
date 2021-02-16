from crawer import craw
from preprocess_scraped_data import get_review_sentiment_dict, clear_scraped_data
from sentiment_analysis import vectorizers_and_predictors, train_models, preprocess, load_model_by_vectorizer_and_predictor, number_to_word_category
import pandas as pd 

if __name__ == "__main__":
    years = [1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020]
    craw(years)
    clear_scraped_data(years)
    crawed_df = get_review_sentiment_dict(years)
    reviews_df = pd.read_csv('train.tsv', delimiter='\t')
    del reviews_df['PhraseId']
    del reviews_df['SentenceId']
    test = pd.read_csv('test.tsv', delimiter='\t')
    train = reviews_df.append(crawed_df)
    train[train.columns[0]] = preprocess(train[train.columns[0]])
    test[test.columns[2]] = preprocess(test[test.columns[2]])
    vectorizers, predictors = vectorizers_and_predictors()
    train_models(train, test, vectorizers, predictors)

    picked_model = load_model_by_vectorizer_and_predictor(vectorizers[2], predictors[2])

    predictions = picked_model.predict([
        preprocess(["Nolan masterfully weaves all these elements together, creating a second act that is breathtaking, suspenseful and thought-provoking...unfortunately, it takes us a good hour for us to get there."])[0],
        preprocess(["...there are few directors operating on Nolan's level within modern-day Hollywood."])[0]
    ])
    
    for prediction in predictions:
        print(number_to_word_category(prediction))
