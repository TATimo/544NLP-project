from __future__ import division
import sys,json,math
import os
import numpy as np
import pprint
import distsim
import time
from operator import itemgetter

def print_result(w_v,key,rank):
##    print "for word:",key,"result is:"
    for i, (word, score) in enumerate(w_v, start=1):
        rank[word] = i
##        print "{}: {} ({})".format(i, word, score)
##    print ""
    return rank

def sim_compare(word_to_vec_dict,w1,w2,w3,w4):
    ans = [0,0,0]
    rank = {}
    ww1 = word_to_vec_dict[w1]
    ww2 = word_to_vec_dict[w2]
    ww4 = word_to_vec_dict[w4]
    ret = distsim.show_nearest(word_to_vec_dict,
                           ww1-w2+ww4,
                           set([w1,w2,w4]),
                           distsim.cossim_dense)
    rank = print_result(ret,ret[0][0],rank)
    if w3 in rank and rank[w3] == 1:
        ans[0] += 1
        ans[1] += 1
        ans[2] += 1
    elif w3 in rank and rank[w3] <= 5 and rank[w3] > 1:
        ans[1] += 1
        ans[2] += 1
    elif w3 in rank and rank[w3] <= 10 and rank[w3] > 5:
        ans[2] += 1
    rinfo = w1+" : "+w2+" :: {} : "+w4
    print rinfo.format(ret[0][0]),'--- Compare:',ret[0][0],w3
    
    return ans

def main():
##    start = time.time()
    word_to_vec_dict = distsim.load_word2vec("nyt_word2vec.4k")
##    word_to_vec_dict = distsim.load_word2vec("glove.6B.300d.txt")
    line_count = 0
    total,o_b,f_b,t_b = 0,0,0,0
    best_v = []
    with open("word-test.v3.txt") as infile:
        for line in infile:
            line_count += 1
            if line_count == 1: continue
            tmpv = line.strip(' \n\t').split()
            if tmpv[0] != ':':
                best_v = sim_compare(word_to_vec_dict,tmpv[0],tmpv[1],tmpv[2],tmpv[3])
                o_b += best_v[0]
                f_b += best_v[1]
                t_b += best_v[2]
                total += 1
            else:
                if(line_count != 2):
                    print '1-best:',o_b/total
                    print '5-best:',f_b/total
                    print '10-best:',t_b/total
                    print ' '
                total,o_b,f_b,t_b = 0,0,0,0
                best_v = []
                print 'For analogy:',tmpv[1]
    print '1-best:',o_b/total
    print '5-best:',f_b/total
    print '10-best:',t_b/total
##    end = time.time()
##    print ' '
##    print 'time is:',str(end - start)+'s'
                
main()
