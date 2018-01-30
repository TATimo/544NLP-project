#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

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

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)



class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()


    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """
##        print(self._pronunciations[word])

        cnt = 0
        if word not in self._pronunciations:
          if word.isalpha() == True: return 1
          else: return 0
        for x in self._pronunciations[word]:
          tmp = 0
          for y in x:
            tmp = tmp + 1 if y[-1].isdigit() else tmp
          cnt = min(cnt,tmp) if cnt > 0 else tmp

        return cnt

    def shrink_word(self,word):
      ans = []
      
      i = 0
      while not word[i][-1].isdigit() and i < len(word) - 1:
        i += 1
        
      return word[i:]

    def rhymes(self, word1, word2):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """

        ans = False
        vowel = ['a','e','i','o','u']

##        print(self._pronunciations[word1])
##        print(self._pronunciations[word2])

        if word1 == "" or word2 == "":
          if word1 in self._pronunciations or word2 in self._pronunciations:
            return True

        if word1 not in self._pronunciations or word2 not in self._pronunciations:
          return False
        
        for i in self._pronunciations[word1]:
          if i[0][-1].isdigit() == False:
            i = self.shrink_word(i)
          for j in self._pronunciations[word2]:
            if j[0][-1].isdigit() == False:
              j = self.shrink_word(j)
##            print i,j
            if len(i) != len(j):
              lw1,lw2,tmpb = len(i) - 1,len(j) - 1,True
              while lw1 >= 0 and lw2 >= 0:
                if i[lw1] != j[lw2]:
                  tmpb = False
                  break
                lw1,lw2 = lw1 - 1,lw2 - 1
              if tmpb == True:
                ans = True
                break
            else:
              if set(i) == set(j):
                ans = True
                break

##        print("***************************************")
        
        return ans

    def remove_punc(self,cnt,line):
      while cnt >= 0:
          if line[cnt] not in punctuation:
            return line[cnt]
            break
          cnt -= 1
      return ""

    def cnt_syll(self,line):
      cnt = 0
      for i in word_tokenize(line):
        cnt += self.num_syllables(i)
      return cnt

    def is_limerick(self, text):
      """
      Takes text where lines are separated by newline characters.  Returns
      True if the text is a limerick, False otherwise.

      A limerick is defined as a poem with the form AABBA, where the A lines
      rhyme with each other, the B lines rhyme with each other, and the A lines do not
      rhyme with the B lines.


      Additionally, the following syllable constraints should be observed:
        * No two A lines should differ in their number of syllables by more than two.
        * The B lines should differ in their number of syllables by no more than two.
        * Each of the B lines should have fewer syllables than each of the A lines.
        * No line should have fewer than 4 syllables

      (English professors may disagree with this definition, but that's what
      we're using here.)


      """
      ttext = text.split("\n")
      ptext = []
      for i in ttext:
        if len(i) > 0 and i[0] != " ": ptext.append(i)

##        for i in ptext:
##          print word_tokenize(i)
##        print "**********************************"

      if len(ptext) != 5:
##          print 0
        return False
              
      A1,A2,B1,B2,A3 = ptext[0],ptext[1],ptext[2],ptext[3],ptext[4]
      sA1,sA2,sB1,sB2,sA3 = self.cnt_syll(A1),self.cnt_syll(A2),self.cnt_syll(B1),self.cnt_syll(B2),self.cnt_syll(A3)

      A1e = self.remove_punc(len(word_tokenize(ptext[0]))-1,word_tokenize(ptext[0]))
      A2e = self.remove_punc(len(word_tokenize(ptext[1]))-1,word_tokenize(ptext[1]))
      B1e = self.remove_punc(len(word_tokenize(ptext[2]))-1,word_tokenize(ptext[2]))
      B2e = self.remove_punc(len(word_tokenize(ptext[3]))-1,word_tokenize(ptext[3]))
      A3e = self.remove_punc(len(word_tokenize(ptext[4]))-1,word_tokenize(ptext[4]))

##      print A1e,A2e,B1e,B2e,A3e
##      print sA1,sA2,sB1,sB2,sA3

      if sA1 < 4 or sA2 < 4 or sA3 < 4 or sB1 < 4 or sB2 < 4:
##        print 1
        return False
      if sB1>=sA1 or sB1>=sA2 or sB1>=sA3 or sB2>=sA1 or sB2>=sA2 or sB2>=sA3:
##        print 2
        return False
      if abs(sA1-sA2) > 2 or abs(sA3-sA2) > 2 or abs(sA1-sA3) > 2 or abs(sB1-sB2) > 2:
##        print 3
        return False
      if self.rhymes(A1e,A2e) == False or self.rhymes(A1e,A3e) == False or self.rhymes(A2e,A3e) == False or self.rhymes(B1e,B2e) == False:
##        print 4
        return False
      if self.rhymes(B1e,A1e) == True or self.rhymes(B1e,A2e) == True or self.rhymes(B1e,A3e) == True or self.rhymes(B2e,A1e) == True or self.rhymes(B2e,A2e) == True or self.rhymes(B2e,A3e) == True:
##        print 5
        return False

##      print 6
      return True

    def apstrophe_tokenize(self,rline):
      pline = word_tokenize(rline)
      ans = []

      for i in range(len(pline)):
        if pline[i] == "n't":
          ans.pop()
          tmp = pline[i-1]+pline[i]
          ans.append(tmp)
        else:
          ans.append(pline[i])
        
      return ans

    def guess_syllables(self,word):
      vowel = ["a","e","i","o","u"]
      cnt = 0

      if word in self._pronunciations: return self.num_syllables(word)
      else:
        for i in word:
          if not i.isalpha():
            return 1
          if i.lower() in vowel: cnt += 1
        
      return cnt

# The code below should not need to be modified
def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')

  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))

if __name__ == '__main__':
  main()
