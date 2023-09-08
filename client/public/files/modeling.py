import os
from model.sbmtm import sbmtm
import graph_tool.all as gt

import csv
import string
import pandas as pd

import spacy
sp = spacy.load('en_core_web_sm')

def clean_string(content):
    cleaned = content.lower()
    tokenized = sp(cleaned)

    stop = ['PRON', 'AUX', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART', 'NUM', 'X', 'INTJ', 'PUNCT']
    return list(filter(lambda w: w != '', 
                       map(lambda w: w.lemma_ if (
                               (w.pos_ not in stop and len(w.text) > 1)
                                   ) else '', 
                           tokenized)))
    # return content.lower(
    #     ).translate(str.maketrans('','', string.punctuation)
    #     ).translate(str.maketrans('—', ' ')
    #     ).encode("ascii", "ignore"
    #     ).decode(
    #     ).split(sep=None)


def run_model():
    path_data = 'client/public/files/'

    filename = os.path.join(path_data, 'simplyrecipes.csv')

    texts = []
    titles = []
    with open(filename,'r', encoding = 'utf8') as f:
        reader = csv.reader(f)
        
        print("Cleaning data")
        next(reader)
        for line in reader:
            texts.append(clean_string(line[1]))
            titles.append(line[0])

    print(texts[0])
    ## we create an instance of the sbmtm-class
    model = sbmtm()

    ## we have to create the word-document network from the corpus
    model.make_graph(texts)

    ## we can also skip the previous step by saving/loading a graph
    # model.save_graph(filename = 'graph.xml.gz')
    # model.load_graph(filename = 'graph.xml.gz')

    ## fit the model
    print("Running model")
    gt.seed_rng(32) ## seed for graph-tool's random number generator --> same results
    model.fit()

    print("Printing clusters")
    model.print_topics(path_save=path_data)

    print("Printing saliency")
    model.print_topic_saliency(path_save=path_data)