#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from csv import DictReader, DictWriter
import string
import nltk
import codecs
import sys
import copy
from nltk.corpus import wordnet as wn
from nltk.tokenize import TreebankWordTokenizer

from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.util import ngrams
from nltk import bigrams
from nltk import trigrams
##from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import itertools
from itertools import tee

kTOKENIZER = TreebankWordTokenizer()

def morphy_stem(word):
    """
    Simple stemmer
    """
    stem = wn.morphy(word)
    if stem:
        return stem.lower()
    else:
        return word.lower()

class FeatureExtractor:
    def __init__(self,lens,lenb,freqs,freqb,poss,posb):
        """
        You may want to add code here
        """
        self.ls = lens
        self.lb = lenb
        self.fs = freqs
        self.fb = freqb
        self.ps = poss
        self.pb = posb
        None

    def features(self, text):
        d = defaultdict(int)
        pre_word = ''
        ppre_word = ''
##        for ii in kTOKENIZER.tokenize(text): txt_set.append(ii.lower())
##        tokens = nltk.word_tokenize(text)
##        tokens = [token.lower() for token in tokens if len(token) > 1]
##        bi_tokens = bigrams(tokens)
##        tri_tokens = trigrams(tokens)
        
        for ii in kTOKENIZER.tokenize(text):
            if ii not in string.punctuation:
     			##Freq words
                if ii in self.fs and ii not in self.fb:
                    d[morphy_stem(ii),ii.lower()[1:5]] += 3
                    d['b'] -= 1
                elif ii in self.fb and ii not in self.fs:
                    d[morphy_stem(ii),ii.lower()[1:5]] += 3
                    d['s'] -= 1
                elif ii in self.fb or self.fs:
                    d[morphy_stem(ii),ii.lower()[1:5]] += 3
                else:
                 	d[morphy_stem(ii),ii.lower()[1:5]] += 1
                ##Length
                if abs(len(text)-self.ls) > abs(len(text)-self.lb):
                    d['s'] += 2.3
                    d['b'] += 1
                elif abs(len(text)-self.ls) < abs(len(text)-self.lb):
                    d['b'] += 2.3
                    d['s'] += 1
            for j in text[-5:-1]:
                if j in string.punctuation:
                    d['b'] += 1
                else:
                    d['s'] += 1

        return d
    
reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')


def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--trainfile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input train file")
    parser.add_argument("--testfile", "-t", nargs='?', type=argparse.FileType('r'), default=None, help="input test file")
    parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")
    parser.add_argument('--subsample', type=float, default=1.0,
                        help='subsample this fraction of total')
    
    args = parser.parse_args()
    trainfile = prepfile(args.trainfile, 'r')
    if args.testfile is not None:
        testfile = prepfile(args.testfile, 'r')
    else:
        testfile = None
    outfile = prepfile(args.outfile, 'w')
    
    # Read in training data
    train = DictReader(trainfile, delimiter='\t')
    
    # Split off dev section
    dev_train = []
    dev_test = []
    full_train = []
    error = []
    allwords_s = []
    allwords_b = []
    posb = []
    poss = []

    it1,it2 = itertools.tee(train)
    lens,lenb,counts,countb = 0,0,0,0
    
    for ii in it1:
        print ii['text'][-5:],ii['cat']
        word = kTOKENIZER.tokenize(ii['text'].lower())
        if ii['cat'] is 's':
            poss.extend([i[1] for i in nltk.pos_tag(word)])
            allwords_s.extend(word)
            counts += 1
            lens += len(ii['text'])
        else:
            posb.extend([i[1] for i in nltk.pos_tag(word)])
            allwords_b.extend(word)
            countb += 1
            lenb += len(ii['text'])

    lens,lenb = lens/counts,lenb/countb
    allwords_s = nltk.FreqDist(allwords_s)
    allwords_b = nltk.FreqDist(allwords_b)
    posb = nltk.FreqDist(posb)
    poss = nltk.FreqDist(poss)

    # Create feature extractor (you may want to modify this)
    fe = FeatureExtractor(lens,lenb,allwords_s,allwords_b,poss,posb)
    
    for ii in it2:
        if args.subsample < 1.0 and int(ii['id']) % 100 > 100 * args.subsample:
            continue
        feat = fe.features(ii['text'])
        if int(ii['id']) % 5 == 0:
            dev_test.append((feat, ii['cat']))
        else:
            dev_train.append((feat, ii['cat']))
        full_train.append((feat, ii['cat']))
    
    # Train a classifier
    sys.stderr.write("Training classifier ...\n")
    classifier = nltk.classify.NaiveBayesClassifier.train(dev_train)

    right = 0
    total = len(dev_test)
    for ii in dev_test:
        prediction = classifier.classify(ii[0])
        if prediction == ii[1]:
            right += 1
        else:
            error.append((ii[1],prediction,ii[0]))
    sys.stderr.write("Accuracy on dev: %f\n" % (float(right) / float(total)))

##    classifier.show_most_informative_features(50)
##    for (tag,guess,txt) in sorted(error):
##        print(tag,guess,txt)
    
    if testfile is None:
        sys.stderr.write("No test file passed; stopping.\n")
    else:
        # Retrain on all data
        classifier = nltk.classify.NaiveBayesClassifier.train(dev_train + dev_test)

        # Read in test section
        test = {}
        for ii in DictReader(testfile, delimiter='\t'):
            test[ii['id']] = classifier.classify(fe.features(ii['text']))

        # Write predictions
        o = DictWriter(outfile, ['id', 'pred'])
        o.writeheader()
        for ii in sorted(test):
            o.writerow({'id': ii, 'pred': test[ii]})


