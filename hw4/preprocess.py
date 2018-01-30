#!/usr/bin/env python

import sys, fileinput
import tree
import itertools
from itertools import tee

def process(mode,fname):
    for line in fname:
        t = tree.Tree.from_str(line)

        # Binarize, inserting 'X*' nodes.
        t.binarize()

        # Remove unary nodes
        t.remove_unit()

        # The tree is now strictly binary branching, so that the CFG is in Chomsky normal form.

        # tree markovization for TOO Specific/ NOT Specific
        if mode == 1:
            t.markovization()
        else:
            t.parentAnnotation()
            
        # Make sure that all the roots still have the same label.
        assert t.root.label == 'TOP'

        print t
    
if __name__ == "__main__":
    it1,it2 = itertools.tee(fileinput.input())
    process(1,it1)
    print '***QifanWang***'
    process(2,it2)
