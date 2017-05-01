#!/usr/bin/env python

from optparse import OptionParser
import os, logging

import re
import string
import itertools
import math


def create_model(path):
    model = {}
    model_tri={}
    f = open(path, 'r')
    lines=""
    for l in f.readlines():
        lines=lines+'$'+l
    lines=lines+'$'
    lines = lines.lower()  # Converts entire text to lower case
    lines = lines.replace(string.punctuation,'')  # removes all special .characters
    lines = re.sub(r"\s+", '$', lines)  # Adds $ to each token like $the$
    set_alpha = string.ascii_letters+"$"
    for a in itertools.combinations_with_replacement(set_alpha, 3):
        bigram = a[0]+a[1]+a[2]
        if model.has_key(bigram):
            continue
        else:
            model[bigram] = math.log((float(lines.count(bigram))+1.0)/(float(lines.count(a[0]+a[1]))+27.0))
    return model

def predict(file, model_en, model_es):
    prediction = ""
    score_en=0.0
    score_es=0.0
    f = open(file, 'r')
    lines = ""
    for l in f.readlines():
        lines = lines + '$' + l
    lines = lines + '$'
    lines = lines.lower()  # Converts entire text to lower case
    lines = lines.replace(string.punctuation, '')  # removes all special .characters
    lines = re.sub(r"\s+", '$', lines)  # Adds $ to each token like $the$
    for i in range(0, len(lines) - 3):
        bigram = lines[i] + lines[i + 1]+lines[i+2]
        if model_en.has_key(bigram):
            score_en+= model_en[bigram]
        else:
            score_en+=math.log(1.0/27.0)
        if model_es.has_key(bigram):
            score_es+=model_es[bigram]
        else:
            score_es+=math.log(1.0/27.0)
    if score_en  > score_es:
        prediction="English"
    else:
        prediction="Spanish"
    return prediction

def main(en_tr, es_tr, folder_te):
    ## STEP 1: create a model for English with file en_tr
    model_en = create_model(en_tr)

    ## STEP 2: create a model for Spanish with file es_tr
    model_es = create_model(es_tr)

    ## STEP 3: loop through all the files in folder_te and print prediction
    folder = os.path.join(folder_te, "en")
    print "Prediction for English documents in test:"
    for f in os.listdir(folder):
        f_path =  os.path.join(folder, f)
        print "%s\t%s" % (f, predict(f_path, model_en, model_es))
    
    folder = os.path.join(folder_te, "es")
    print "\nPrediction for Spanish documents in test:"
    for f in os.listdir(folder):
        f_path =  os.path.join(folder, f)
        print "%s\t%s" % (f, predict(f_path, model_en, model_es))

if __name__ == "__main__":
    usage = "usage: %prog [options] EN_TR ES_TR FOLDER_TE"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 3:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    main(args[0], args[1], args[2])


