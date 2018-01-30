#!/usr/bin/env python

from __future__ import division
import sys, fileinput, time, math, tree
import itertools

Testset = []
Flag,theta = 0,1
# Sibling
Allrules = {}
Words = {}
Probrules = {}
# Parent
NewAllrules = {}
NewWords = {}
NewProbrules = {}

def learnCFG(path,Ar,W,Pr,mode):
##    path = "./train.Fintrees.pre.unk"
    switch = False
    for line in open(path):
        if mode == 1:
            if line.strip() == '***QifanWang***': break;
        elif mode == 2:
            if line.strip() == '***QifanWang***':
                switch = True
                continue
            if not switch:
                continue
        t = tree.Tree.from_str(line)
        for node in t.bottomup():
            crule = ''
            if not len(node.children): continue
            #init each node in rules dic
            if node.label not in Ar: Ar[node.label] = {}
            #collect the words with possible tag
            if len(node.children) == 1:
                if node.children[0].label not in W: W[node.children[0].label] = set()
                W[node.children[0].label].add(node.label)
            #collect all possible child
            for child in node.children:
                crule += child.label + ' '
            crule = crule[:-1]
            #add occur time
            if crule not in Ar[node.label]: Ar[node.label][crule] = 1
            else: Ar[node.label][crule] += 1
    #convert occur time to occur probility for Viterbi algorithm
    for rule in Ar:
        rule_sum = 0
        rules = Ar[rule]
        if rule not in Pr: Pr[rule] = {}
        for i in rules:
            rule_sum += rules[i]
            if i not in Pr[rule]: Pr[rule][i] = 0
        for i in rules:
            Pr[rule][i] = rules[i]/rule_sum

def SmoothLearnCFG(path,Ar,W,Pr,mode):
##    path = "./train.Fintrees.pre.unk"
    switch = False
    for line in open(path):
        if mode == 1:
            if line.strip() == '***QifanWang***': break;
        elif mode == 2:
            if line.strip() == '***QifanWang***':
                switch = True
                continue
            if not switch:
                continue
        t = tree.Tree.from_str(line)
        for node in t.bottomup():
            crule = ''
            if not len(node.children): continue
            #init each node in rules dic
            if node.label not in Ar: Ar[node.label] = {}
            #collect the words with possible tag
            isword = len(node.children) == 1
            if isword:
                if node.children[0].label not in W: W[node.children[0].label] = set()
                if node.children[0].label != '<unk>': W[node.children[0].label].add(node.label)
            #collect all possible child
            for child in node.children:
                crule += child.label + ' '
            crule = crule[:-1]
            #add occur time
            if crule not in Ar[node.label]:
                if crule == '<unk>': Ar[node.label][crule] = theta
                else: Ar[node.label][crule] = 1 if not isword else 1 + theta
            else:
                if crule != '<unk>': Ar[node.label][crule] += 1
    #Smoothing Probilities for unknown words
    for r in Ar:
        W['<unk>'].add(r)
        Ar[r]['<unk>'] = theta
    #convert occur time to occur probility for Viterbi algorithm
    for rule in Ar:
        rule_sum = 0
        rules = Ar[rule]
        if rule not in Pr: Pr[rule] = {}
        for i in rules:
            rule_sum += rules[i]
            if i not in Pr[rule]: Pr[rule][i] = 0
        for i in rules:
            Pr[rule][i] = rules[i]/rule_sum

class ViterbiGo():
    def __init__(self,Ar_in,W_in,Pr_in,NewAr_in,NewW_in,NewPr_in):
        self.Arin = Ar_in
        self.Win = W_in
        self.Prin = Pr_in
        self.NArin = NewAr_in
        self.NWin = NewW_in
        self.NPrin = NewPr_in
    
    def Viterbi(self,fname):
        for line in open(fname): self.parsing(line,0)
        
    def parsing(self,line,mode):
        if mode == 1:
            Ar = self.Arin
            W = self.Win
            Pr = self.Prin
        elif mode == 0:
            Ar = self.NArin
            W = self.NWin
            Pr = self.NPrin
        
        w = line.split()
        Vchart = {} #2D chart of Viterbi
        found_1 = False
        found_2 = False

        #construct 2D char of Viterbi
        for i in xrange(0,len(w)):
            word = ['<unk>',w[i]] if w[i] not in W else w[i]
            for j in xrange(i+1,len(w)+1):
                Vchart[(i,j)] = {}
            ii = W[word] if type(word) == str else W[word[0]]
            for k in ii:
                kk = Pr[k][word] if type(word) == str else Pr[k][word[0]]
                if k not in Vchart[(i,i+1)]: Vchart[(i,i+1)][k] = ('',0)
                if kk > Vchart[(i,i+1)][k][1]:
##                    Vchart[(i,i+1)][k] = (word,kk) if type(word) == str else (word[0],kk)
                    Vchart[(i,i+1)][k] = (word,kk)

        #work through Viterbi Chart
        inlen = len(w)
        for loop in xrange(0,inlen - 1):
            for i in xrange(0,inlen - 1 - loop):
                j = loop + i + 2
                for k in xrange(i,j):
                    if i >= i+j-k or j <= i+j-k or len(Vchart[(i,i+j-k)]) == 0 or len(Vchart[(i+j-k,j)]) == 0: continue
                    for rule in Ar:
                        for rc in Ar[rule]:
                            r = rc.split()
                            if len(r) == 1: continue
                            found1 = r[0] in Vchart[(i,i+j-k)] and r[1] in Vchart[(i+j-k,j)]
                            if found1:
                                if rule not in Vchart[(i,j)]: Vchart[(i,j)][rule] = ((('',''),0),0)
                                base_prob = Pr[rule][rc]
                                max_prob = 0
                                if found1:
                                    max_prob = base_prob * Vchart[(i,i+j-k)][r[0]][1] * Vchart[(i+j-k,j)][r[1]][1]
                                if max_prob > Vchart[(i,j)][rule][1]:
                                    Vchart[(i,j)][rule] = (((r[0],r[1]),i+j-k),max_prob)
                                    
##        print (self.back_tracking(Vchart,0,len(w),'TOP','') if 'TOP' in Vchart[(0,len(w))] else '')
        if 'TOP' in Vchart[(0,len(w))]:
            print (self.back_tracking(Vchart,0,len(w),'TOP',''))
        else:
            if mode == 0: self.parsing(line,1)
            elif mode == 1: print ''                  

    def back_tracking(self,Vchart,i,j,rule,sent):
        if type(Vchart[(i,j)][rule][0]) == tuple:
            sent += '(' + rule + ' '
            sent = self.back_tracking(Vchart, i, Vchart[(i,j)][rule][0][1], Vchart[(i,j)][rule][0][0][0],sent) + ' '
            sent = self.back_tracking(Vchart, Vchart[(i,j)][rule][0][1], j, Vchart[(i,j)][rule][0][0][1],sent) + ')'
        else:
            if type(Vchart[(i,j)][rule][0]) == str: sent += '(' + rule + ' ' + Vchart[(i,j)][rule][0] + ')'
            else: sent += '(' + rule + ' ' + Vchart[(i,j)][rule][0][1] + ')'
        return sent
    
if __name__ == "__main__":
    try:
        _, trainfile, testfile = sys.argv
    except:
        sys.stderr.write("usage: Q5.py <train-file> <test-file>\n")
        sys.exit(1)
        
    if testfile == 'dev.strings':    
        learnCFG(trainfile,Allrules,Words,Probrules,1)
        learnCFG(trainfile,NewAllrules,NewWords,NewProbrules,2)
    else:
        SmoothLearnCFG(trainfile,Allrules,Words,Probrules,1)
        SmoothLearnCFG(trainfile,NewAllrules,NewWords,NewProbrules,2)
    V = ViterbiGo(Allrules,Words,Probrules,NewAllrules,NewWords,NewProbrules)
    V.Viterbi(testfile)
