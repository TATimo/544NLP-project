import sys
import tree
from operator import itemgetter

all_rules = {}
Probrules = {}
rules_count = []

def learnCFG():
    for line in open("./train.trees.pre.unk"):
        t = tree.Tree.from_str(line)
        for node in t.bottomup():
            crule = ''
            if not len(node.children): continue
            #init each node in rules dic
            if node.label not in all_rules: all_rules[node.label] = {}
            #collect all possible child
            for child in node.children:
                crule += child.label + ' '
            crule = crule[:-1]
            #add occur time
            if crule not in all_rules[node.label]: all_rules[node.label][crule] = 1
            else: all_rules[node.label][crule] += 1
    #append all rules into list then sort
    ruleNum = 0
    for i in all_rules:
        ii = all_rules[i]
        for j in ii:
             rules_count.append(((i,j),ii[j]))
             ruleNum += 1
    top_five = sorted(rules_count, key=itemgetter(1), reverse=True)
    #print info
    print 'Total Rules Used:',ruleNum
    print 'Most Frequent Rules:'
    for i in xrange(1):
        print '  ' + top_five[i][0][0] + ' -> ' + top_five[i][0][1] + ' # ' + str(top_five[i][1])
    #convert to probilities
    for rule in all_rules:
        rule_sum = 0
        rules = all_rules[rule]
        if rule not in Probrules: Probrules[rule] = {}
        for i in rules:
            rule_sum += rules[i]
            if i not in Probrules[rule]: Probrules[rule][i] = 0
        for i in rules:
            Probrules[rule][i] = rules[i]/rule_sum

if __name__ == "__main__":
    learnCFG()
