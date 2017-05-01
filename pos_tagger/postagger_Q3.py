#!/usr/bin/env python

from optparse import OptionParser
import os, logging

import math
from scipy.stats import mode
import utils
from nltk.corpus import wordnet

def create_model(sentences):
    words = {}
    tags = {}
    tag_list = []
    word_tag = {}
    tag_model = {}
    word_tagmost={}
    for sentence in sentences:
        for token in sentence:
            #token.word = token.word.lower()
            if not word_tagmost.has_key(token.word):
                word_tagmost[token.word]=[]
            word_tagmost[token.word].append(token.tag)
    #model = str(max(set(tags), key=tags.count))
    for k in word_tag:
        max_tag= str(mode(word_tagmost[k])[0])
        word_tagmost[k]=max_tag

    for sentence in sentences:
        for token in sentence:
            if not words.has_key(token.word):
                words[token.word] = 1
            else:
                words[token.word] += 1
            if not tags.has_key(token.tag):
                tags[token.tag] = 1
            else:
                tags[token.tag] += 1
            tag_list.append(token.tag)
            wordtag = str(token.word) + "|" + str(token.tag)
            if not word_tag.has_key(wordtag):
                word_tag[wordtag] = 1
            else:
                word_tag[wordtag] += 1

    tags_counts = {}
    for k in range(0, len(tag_list) - 1):
        if tags_counts.has_key(str(tag_list[k]) + "|" + str(tag_list[k + 1])):
            tags_counts[str(tag_list[k]) + "|" + str(tag_list[k + 1])] += 1
        else:
            tags_counts[str(tag_list[k]) + "|" + str(tag_list[k + 1])] = 1

    for i in range(0, len(tag_list) - 1):
        tag_bigram = str(tag_list[i]) + "|" + str(tag_list[i + 1])
        if tag_model.has_key(tag_bigram):
            continue
        else:
            tag_model[tag_bigram] =(float(tags_counts[tag_bigram]) + 1.0) / ((float(tags[tag_list[i]])) + len(tags.keys()))

    word_tag_model = {}

    for w in words.keys():
        for t2 in tags.keys():
            w_t=str(w)+"|"+str(t2)
            if word_tag.has_key(w_t):
                word_tag_model[w_t]=float(float(word_tag[w_t])) / (float(tags[t2]) )
            else:
                word_tag_model[w_t]=0.0

    return [tag_model, word_tag_model, tags, words,word_tagmost]


def predict_tags(sentences, model):
    for sentence in sentences:
        for token in sentence:
            if token == sentence[0]:
                max_prev = [1.0, "<s>"]
                token.tag = "<s>"
            else:
                if model[3].has_key(token.word):
                    curr_ver = [None, "<UNK>"]
                    for t in model[2].keys():
                        w_t = str(token.word) + "|" + str(t)
                        #if model[1][w_t] > 0.0:
                        #    print model[1][w_t]
                        t_t1 = str(max_prev[1]) + "|" + str(t)
                        if model[0].has_key(t_t1):
                                    viterbi = float(max_prev[0] * model[1][w_t] * model[0][t_t1])
                                    #print model[0][t_t1]
                        else:
                                    viterbi = float(max_prev[0] * model[1][w_t] * float(1.0/float(model[2][max_prev[1]]+len(model[2].keys()))))
                                    #print viterbi
                        #print viterbi
                        if viterbi >= curr_ver[0] or curr_ver[0] is None:
                            curr_ver = [viterbi, t]
                    max_prev = curr_ver
                    #print curr_ver
                    token.tag = max_prev[1]
                else:
                    max_prev = [1.0, "NN"]
                    for i,j in enumerate(wordnet.synsets(str(token.word).lower())):
                        for w in j.lemma_names:
                            if model[4].has_key(w):
                                max_prev = [1.0, str(model[4][w][0])]
                                break
                            else:
                                max_prev = [1.0, "NN"]
                    #print max_prev
                    #raw_input()
                    token.tag = max_prev[1]
                    #print "here"
            #print token.tag
            #raw_input()
    return sentences


if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD TEST"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    training_file = args[0]
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    test_sents = utils.read_tokens(test_file)

    model = create_model(training_sents)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(training_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(training_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)
