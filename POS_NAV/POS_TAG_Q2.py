#!/usr/bin/env python

from optparse import OptionParser
import os, logging, math
import utils
from scipy.stats import mode
import nltk

patterns = [
     (r'.*ing$', 'VBG'),
     (r'.*ed$', 'VBD'),
     (r'.*es$', 'VBZ'),
     (r'.*ould$', 'MD'),
     (r'.*\'s$', 'NN$'),
     (r'.*s$', 'NNS'),
     (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),  # cardinal num.
     (r'.*', 'NN')         # nouns (default)
]
regexp_tagger = nltk.RegexpTagger(patterns)

def create_model(sentences):
    words = {}
    tags = {}
    word_tag={}
    tags_tags={}
    word_tag_prob={}
    tags_tags_prob={}
    model = {}
    for sentence in sentences:
        for token in sentence:
            if not model.has_key(token.word):
                model[token.word]=[]
            model[token.word].append(token.tag)
    for w in model.keys():
        model[w]=mode(model[w])[0]

    for sentence in sentences:
        for i in range(0,len(sentence)):
            #Word Counts when each word is encountered
            if words.has_key(sentence[i].word):
                words[sentence[i].word]+=1
            else:
                words[sentence[i].word]=1
            #Tag Counts when each tag is encountered
            if tags.has_key(sentence[i].tag):
                tags[sentence[i].tag]+=1
            else:
                tags[sentence[i].tag]=1

            tag_word = str(sentence[i].word)+"|"+str(sentence[i].tag)
            #Count of each word tag
            if word_tag.has_key(tag_word):
                word_tag[tag_word]+=1
            else:
                word_tag[tag_word]=1

            if i < len(sentence)-1:
                tag_tag = str(sentence[i].tag)+"|"+str(sentence[i+1].tag)
                #Count of tagsets
                if tags_tags.has_key(tag_tag):
                    tags_tags[tag_tag]+=1
                else:
                    tags_tags[tag_tag]=1

    print("Counts completeted. Calculating Probabilities")
    #Calculating probability of tag tag set
    for t1 in tags.keys():
        for t2 in tags.keys():
            tag_tagset=str(t1)+"|"+str(t2)
            if tags_tags.has_key(tag_tagset):
                tags_tags_prob[tag_tagset]=float(tags_tags[tag_tagset]+1.0)/float(tags[t1]+len(tags.keys()))
            else:
                tags_tags_prob[tag_tagset]=float(1.0/float(tags[t1]+len(tags.keys())))
    print("tag tag completeted. Calculating word tag")

    model_f = [tags_tags_prob,word_tag,tags,model]
    print ("Model Created Successfully. Going to test Data.")
    return model_f

def predict_tags(sentences, model):
    for sentence in sentences:
        for token in sentence:
            if token.word == sentence[0].word:
                vit_prev = [1.0,"<s>"]
            elif not model[3].has_key(token.word):
                vit_prev = [1.0,regexp_tagger.tag(token.word)[0][1]]
            else:
                cur_v = [None,"UNK"]
                for tag1 in model[2].keys():
                    key1=str(token.word)+"|"+str(tag1)
                    key2 = str(vit_prev[1]) + "|" + str(tag1)
                    if model[1].has_key(key1):
                        w_t = (float(model[1][key1])/float(model[2][tag1]))
                    else:
                        w_t = 0.0
                    v = w_t*model[0][key2]*vit_prev[0]
                    v = [v,tag1]
                    if v[0] >cur_v[0] or cur_v[0] is None:
                        cur_v = v
                vit_prev = cur_v
            token.tag = str(vit_prev[1])
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
    print "Accuracy in testing [%s sentences]: %s" % (len(sents), accuracy)
