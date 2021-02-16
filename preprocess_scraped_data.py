import os
from os import walk
import json
import pandas as pd

fileDir = os.path.dirname(os.path.realpath('__file__'))

def clear_scraped_data(years):
    for year in years:
        _, _, filenames = next(walk(os.path.join(fileDir, str(year))))
        for filename in filenames:
            if not filename.endswith('json'):
                os.remove(os.path.join(fileDir, f'{year}\\{filename}'))
                continue
            read_file =  open(os.path.join(fileDir, f'{year}\\{filename}'), "r")
            info = json.load(read_file)
            read_file.close()
            if info == None:
                os.remove(os.path.join(fileDir, f'{year}\\{filename}'))

def process_rating_score(score):
    score_split_str = score.split('/')
    score_split = [float(score_split_str[0]), float(score_split_str[1])]
    res = -1
    if (score_split[1] == 5):
        res = round(score_split[0])
    elif (score_split[1] > 5):
        res = round(score_split[0]/(score_split[1]/5))
    else:
        res = round(score_split[1]*(5/score_split[1]))
    return res - 1 if res != 0 else 0

def get_review_sentiment_dict(years):
    review_sentiment_dict = dict()
    review_sentiment_dict['Phrase'] = list()
    review_sentiment_dict['Sentiment'] = list()
    for year in years:
        _, _, filenames = next(walk(os.path.join(fileDir, str(year))))
        for filename in filenames:
            read_file = open(os.path.join(fileDir, f'{year}\\{filename}'), "r")
            info = json.load(read_file)                
            try:
                for review, score in zip((info['reviews'])['reviews'], (info['reviews'])['rating']):
                    if score != None and score != '' and review != None and review != '':
                        review_sentiment_dict['Phrase'].append(review)
                        review_sentiment_dict['Sentiment'].append(process_rating_score(score))
            except:
                if len(review_sentiment_dict['Phrase']) > len(review_sentiment_dict['Sentiment']):
                    review_sentiment_dict['Phrase'].pop()
                elif len(review_sentiment_dict['Phrase']) < len(review_sentiment_dict['Sentiment']):
                    review_sentiment_dict['Phrase'].pop()
                continue
    return pd.DataFrame.from_dict(review_sentiment_dict)
