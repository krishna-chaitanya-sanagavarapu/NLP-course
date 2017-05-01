#!/usr/bin/env python

from optparse import OptionParser
from scipy.stats import mode
import os, logging
import utils

def create_model(sentences):
    model = {}
    for sentence in sentences:
        for token in sentence:
            if not model.has_key(token.word):
                model[token.word]=[]
            model[token.word].append(token.tag)
    for w in model.keys():
        model[w]=mode(model[w])[0]
    return model

def predict_tags(sentences, model):
    for sentence in sentences:
        for token in sentence:
            if model.has_key(token.word):
                token.tag = model[token.word]
            else:
                token.tag = "NN"
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
