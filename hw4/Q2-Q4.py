from __future__ import division
import sys, fileinput, time, math, tree
import matplotlib.pyplot as plt

Testset = []
py = []
px = []
Flag = 0
switch = False
Allrules = {}
words = {}
Probrules = {}

def learnCFG():
    for line in open("./train.trees.pre.unk"):
        t = tree.Tree.from_str(line)
        for node in t.bottomup():
            crule = ''
            if not len(node.children): continue
            #init each node in rules dic
            if node.label not in Allrules: Allrules[node.label] = {}
            #collect the words with possible tag
            if len(node.children) == 1:
                if node.children[0].label not in words: words[node.children[0].label] = set()
                words[node.children[0].label].add(node.label)
            #collect all possible child
            for child in node.children:
                crule += child.label + ' '
            crule = crule[:-1]
            #add occur time
            if crule not in Allrules[node.label]: Allrules[node.label][crule] = 1
            else: Allrules[node.label][crule] += 1
    #convert occur time to occur probility for Viterbi algorithm
    for rule in Allrules:
        rule_sum = 0
        rules = Allrules[rule]
        if rule not in Probrules: Probrules[rule] = {}
        for i in rules:
            rule_sum += rules[i]
            if i not in Probrules[rule]: Probrules[rule][i] = 0
        for i in rules:
            Probrules[rule][i] = rules[i]/rule_sum

class ViterbiGo():
    def __init__(self):
         pass
    
    def Viterbi(self,fname):
        for line in fname: self.parsing(line)
        
    def parsing(self,line):
        start = time.time() #start counting time
        w = line.split()
        Vchart = {} #2D chart of Viterbi
        found_1 = False
        found_2 = False

        #construct 2D char of Viterbi
        for i in xrange(0,len(w)):
            word = ['<unk>',w[i]] if w[i] not in words else w[i]
            for j in xrange(i+1,len(w)+1):
                Vchart[(i,j)] = {}
            ii = words[word] if type(word) == str else words[word[0]]
            for k in ii:
                kk = Probrules[k][word] if type(word) == str else Probrules[k][word[0]]
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
                    for rule in Allrules:
                        for rc in Allrules[rule]:
                            r = rc.split()
                            if len(r) == 1: continue
                            found1 = r[0] in Vchart[(i,i+j-k)] and r[1] in Vchart[(i+j-k,j)]
                            if found1:
                                if rule not in Vchart[(i,j)]: Vchart[(i,j)][rule] = ((('',''),0),0)
                                base_prob = Probrules[rule][rc]
                                max_prob = 0
                                if found1:
                                    max_prob = base_prob * Vchart[(i,i+j-k)][r[0]][1] * Vchart[(i+j-k,j)][r[1]][1]
                                    switch = False
                                if max_prob > Vchart[(i,j)][rule][1]:
                                    Vchart[(i,j)][rule] = (((r[0],r[1]),i+j-k),max_prob)
                                    
        end = time.time() #counting time end
        print (self.back_tracking(Vchart,0,len(w),'TOP','') if 'TOP' in Vchart[(0,len(w))] else '')
        
##        x,y = str(math.log(len(w))),str(math.log(1000*(end - start)))
##        px.append(x)
##        py.append(y)

    def back_tracking(self,Vchart,i,j,rule,sent):
        if type(Vchart[(i,j)][rule][0]) == tuple:
##            sent += '(' + rule + ' ' + str(math.log(Vchart[(i,j)][rule][1],10)) + ' '
            sent += '(' + rule + ' '
            sent = self.back_tracking(Vchart, i, Vchart[(i,j)][rule][0][1], Vchart[(i,j)][rule][0][0][0],sent) + ' '
            sent = self.back_tracking(Vchart, Vchart[(i,j)][rule][0][1], j, Vchart[(i,j)][rule][0][0][1],sent) + ')'
        else:
##            if type(Vchart[(i,j)][rule][0]) == str: sent += '(' + rule + ' ' + str(math.log(Vchart[(i,j)][rule][1],10)) + ' ' + Vchart[(i,j)][rule][0] + ')'
##            else: sent += '(' + rule + ' ' + str(math.log(Vchart[(i,j)][rule][1],10)) + ' ' + Vchart[(i,j)][rule][0][1] + ')'
            if type(Vchart[(i,j)][rule][0]) == str: sent += '(' + rule +' ' + Vchart[(i,j)][rule][0] + ')'
            else: sent += '(' + rule + ' ' + Vchart[(i,j)][rule][0][1] + ')'
        return sent
    
if __name__ == "__main__":
    learnCFG()
    V = ViterbiGo()
    V.Viterbi(fileinput.input())

##    plt.plot(px,py,'ro')
##    plt.plot([-3.5,-0.5,2.5,5.5])
##    plt.ylabel('parsing time')
##    plt.xlabel('sentence length')
##    plt.show()
