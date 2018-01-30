import numpy as np
from numpy import random
from numpy import array

def run_viterbi(emission_scores, trans_scores, start_scores, end_scores):
    """Run the Viterbi algorithm.

    N - number of tokens (length of sentence)
    L - number of labels

    As an input, you are given:
    - Emission scores, as an NxL array
    - Transition scores (Yp -> Yc), as an LxL array
    - Start transition scores (S -> Y), as an Lx1 array
    - End transition scores (Y -> E), as an Lx1 array

    You have to return a tuple (s,y), where:
    - s is the score of the best sequence
    - y is a size N array of integers representing the best sequence.
    """

    L = start_scores.shape[0]
    assert end_scores.shape[0] == L
    assert trans_scores.shape[0] == L
    assert trans_scores.shape[1] == L
    assert emission_scores.shape[1] == L
    N = emission_scores.shape[0]

    SS = start_scores.shape
    ES = emission_scores.shape
    y = []

    #create a 2D arrays with numpy function
    viterbi = np.zeros(ES)
    viterbi.fill(-100000)
    bPtr = np.zeros(ES, dtype = int)

    #init all arrays
    for i in xrange(L):
        bPtr[0][i] = -1
        viterbi[0][i] = start_scores[i] + emission_scores[0][i]

    #viterbi algorithm
    for i in xrange(1,N):
        for j in xrange(L):
            for k in xrange(L):
                current_score = viterbi[i-1][k] + trans_scores[k][j] + emission_scores[i][j]
                if current_score > viterbi[i][j]:
                    viterbi[i][j] = current_score
                    bPtr[i][j] = k

    f_score = -10000
    f_pos = 0
    for i in xrange(L):
        tmpv = end_scores[i] + viterbi[N-1][i]
        if tmpv > f_score:
            f_score = tmpv
            f_pos = i
            
    y.append(f_pos)

    for i in xrange(N - 1, 0, -1):
        y.append(bPtr[i][f_pos])
        f_pos = bPtr[i][f_pos]

    return (f_score, y[::-1])
