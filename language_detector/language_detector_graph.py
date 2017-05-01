#!/usr/bin/env python

from optparse import OptionParser
import os, logging
import numpy as np
import re
import string
import math
import matplotlib.pyplot as plt

def create_model(path,k):
    model = {}
    f = open(path, 'r')
    lines=""
    for l in f.readlines():
        if len(lines.split(' '))<=k:
            lines=lines+'$'+l
    lines=lines+'$'
    lines = lines.lower()  # Converts entire text to lower case
    lines = lines.replace(string.punctuation,'')  # removes all special .characters
    lines = re.sub(r"\s+", '$', lines)  # Adds $ to each token like $the$
    for i in range(0,len(lines)-2):
        bigram=lines[i]+lines[i+1]
        if model.has_key(bigram):
            continue
        else:
            model[bigram] = math.log((float(lines.count(bigram))+1.0)/(float(lines.count(lines[i]))+27.0))

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
    for i in range(0, len(lines) - 2):
        bigram = lines[i] + lines[i + 1]
        if model_en.has_key(bigram):
            score_en+=model_en[bigram]
        else:
            score_en+=math.log((1.0/26.0))
        if model_es.has_key(bigram):
            score_es+=model_es[bigram]
        else:
            score_es+=math.log((1.0/26.0))
        if score_en>score_es:
            prediction="English"
        else:
            prediction="Spanish"
    return prediction,score_en,score_es

def main(en_tr, es_tr, folder_te):

    escores_en=[]
    escores_es=[]
    sscores_en=[]
    sscores_es=[]
    k_arr=[]
    fle_fr_tokens=open("tok_test2.csv",'w')
    file_prob = open("fr_graph.csv",'w')
    for k in range(100,10000,500):
        k_arr.append(k)
        ## STEP 1: create a model for English with file en_tr
        model_en = create_model(en_tr,k)

        ## STEP 2: create a model for Spanish with file es_tr
        model_es = create_model(es_tr,k)

        ## STEP 3: loop through all the files in folder_te and print prediction
        folder = os.path.join(folder_te, "en")

        enscr,esscr= 0.0,0.0
        f_count=0.0
        fle_fr_tokens.write("Prediction for English documents in test:")
        for f in os.listdir(folder):
            f_count+=1.0
            f_path =  os.path.join(folder, f)
            prediction,score_eng,score_span=predict(f_path, model_en, model_es)
            fle_fr_tokens.write(str(k)+","+str(f)+","+str(prediction)+","+str(score_eng)+","+str(score_span)+"\n")
            enscr+=score_eng
            esscr+=score_span
        file_prob.write(str(k) + "," + str(enscr/f_count) + "," + str(esscr/f_count))
        escores_en.append(abs(enscr)/f_count)
        escores_es.append(abs(esscr)/f_count)
        folder = os.path.join(folder_te, "es")


        enscr, esscr = 0.0, 0.0
        f_count = 0.0
        fle_fr_tokens.write("\nPrediction for Spanish documents in test:")
        for f in os.listdir(folder):
            f_count+=1.0
            f_path =  os.path.join(folder, f)
            prediction,score_eng,score_span=predict(f_path, model_en, model_es)
            fle_fr_tokens.write(str(k) + "," + str(f) + "," + str(prediction) + "," + str(score_eng) + "," + str(score_span)+"\n")
            enscr += score_eng
            esscr += score_span
        sscores_en.append(enscr/f_count)
        sscores_es.append(esscr/f_count)
        file_prob.write(str(enscr/f_count)+","+str(esscr/f_count)+"\n")
    #plt.bar(k_arr,escores_en,align='center')
    bar_width = 0.35

    opacity = 0.4
    error_config = {'ecolor': '0.3'}
    index = np.arange(len(k_arr))
    rects1 = plt.bar(k_arr, escores_en, bar_width,
                     alpha=opacity,
                     color='b',
                     yerr=k_arr)
    #plt.bar(k_arr,escores_es,0.35)
    plt.show()
    #plt.bar(k_arr,sscores_en,0.35)
    #plt.show()
    #plt.bar(k_arr,sscores_es,0.35)
    #plt.show()

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

