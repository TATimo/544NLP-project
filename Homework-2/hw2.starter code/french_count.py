import sys
from fst import FST
from fsmutils import composewords

kFRENCH_TRANS = {0: "zero", 1: "un", 2: "deux", 3: "trois", 4:
                 "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit",
                 9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13:
                 "treize", 14: "quatorze", 15: "quinze", 16: "seize",
                 20: "vingt", 30: "trente", 40: "quarante", 50:
                 "cinquante", 60: "soixante", 100: "cent"}

kFRENCH_AND = 'et'

def prepare_input(integer):
    assert isinstance(integer, int) and integer < 1000 and integer >= 0, \
      "Integer out of bounds"
    if integer != 0: return list("%03i" % integer)
    else: return list('z')
## Modify this func to achieve 0 situation

def french_count():    
    f = FST('french')

    f.add_state('start')
    f.add_state('z')
    for i in range(30):
        f.add_state(str(i))

    f.initial_state = ('start')

    for i in range(20,30):
        f.set_final(str(i))
    f.set_final('z')

    f.add_arc('start', 'z', ['z'], [kFRENCH_TRANS[0]])
    
    for i in range(10):
        f.add_arc('start', str(i), [str(i)], [])
        for j in range(10,20):
            if i is 0:
                f.add_arc(str(i), str(j), [str(j-10)], [])
            elif i is 1:
                f.add_arc(str(i), str(j), [str(j-10)], [kFRENCH_TRANS[100]])
            elif i in range(2,10):
                f.add_arc(str(i), str(j), [str(j-10)], [kFRENCH_TRANS[i],kFRENCH_TRANS[100]])

    for i in range(10,20):
        for j in range(20,30):
            if i is 10:
                if j!= 20: f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[j-20]])
                else: f.add_arc(str(i), str(j), [str(j-20)], [])
            elif i is 11 and j in range(20,27):
                f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[j-10]])
            elif i is 11 and j in range(27,30):
                f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[10],kFRENCH_TRANS[j-20]])
            elif i in range(12,17):
                if j is 20:
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[int(i%10)*10]])
                elif j is 21:
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[int(i%10)*10],kFRENCH_AND,kFRENCH_TRANS[1]])
                else:
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[int(i%10)*10],kFRENCH_TRANS[j-20]])
            elif i is 17:
                if j is 20:
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[60],kFRENCH_TRANS[10]])
                elif j is 21:
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[60],kFRENCH_AND,kFRENCH_TRANS[11]])
                elif j in range(22,27):
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[60],kFRENCH_TRANS[j-10]])
                elif j in range(27,30):
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[60],kFRENCH_TRANS[10],kFRENCH_TRANS[j-20]])
            elif i is 18:
                if j is 20:
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[4],kFRENCH_TRANS[20]])
                elif j in range(21,30):
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[4],kFRENCH_TRANS[20],kFRENCH_TRANS[j-20]])
            elif i is 19:
                if j in range(20,27):
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[4],kFRENCH_TRANS[20],kFRENCH_TRANS[j-10]])
                elif j in range(27,30):
                    f.add_arc(str(i), str(j), [str(j-20)], [kFRENCH_TRANS[4],kFRENCH_TRANS[20],kFRENCH_TRANS[10],kFRENCH_TRANS[j-20]])

    return f

if __name__ == '__main__':
    string_input = raw_input()
    user_input = int(string_input)
##    f = french_count()
##    file = open('french_numbers.txt', 'r')
##    lines = file.read().split('\n')
##    for line in lines:
##        token = line.split(':')
##        try: output = " ".join(f.transduce(prepare_input(int(token[0].strip()))))
##        except: print "error_input: " + token[0].strip()
##        if output != token[1].strip().lower():
##           print token[0].strip() + " incorrect, program output " + output + ", expect " + token[1].strip()
    if string_input:
        print user_input, '-->',
        print " ".join(f.transduce(prepare_input(user_input)))
