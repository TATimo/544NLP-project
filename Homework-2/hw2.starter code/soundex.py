from fst import FST
import string, sys
from fsmutils import composechars, trace

def letters_to_numbers():
    """
    Returns an FST that converts letters to numbers as specified by
    the soundex algorithm
    """
##    tmp = raw_input().strip()
    avoid = ["a","e","i","o","u","h","w","y"]
    g1 = ["b","f","p","v"]
    g2 = ["c","g","j","k","q","s","x","z"]
    g3 = ["d","t"]
    g4 = ["l"]
    g5 = ["m","n"]
    g6 = ["r"]
    
    # Let's define our first FST
    f1 = FST('soundex-generate')

    # Indicate that '1' is the initial state
    f1.add_state('start')
    f1.add_state('1')
    f1.add_state('2')
    f1.add_state('3')
    f1.add_state('4')
    f1.add_state('5')
    f1.add_state('6')
    f1.add_state('7')
    f1.initial_state = 'start'

    # Set all the final states
    f1.set_final('1')
    f1.set_final('2')
    f1.set_final('3')
    f1.set_final('4')
    f1.set_final('5')
    f1.set_final('6')
    f1.set_final('7')

    # Add the rest of the arcs
    for letter in string.ascii_lowercase:
        if letter in avoid:
            f1.add_arc('start', '7', (letter), (letter))
            f1.add_arc('start', '7', (letter.upper()), (letter.upper()))
            f1.add_arc('7', '7', (letter), ())
            for i in ['1','2','3','4','5','6']:
                f1.add_arc(i, '7', (letter), ())
        elif letter in g1:
            f1.add_arc('start', '1', (letter), (letter))
            f1.add_arc('start', '1', (letter.upper()), (letter.upper()))
            f1.add_arc('1', '1', (letter), ())
            for i in ['7','2','3','4','5','6']:
                f1.add_arc(i, '1', (letter), ('1'))
        elif letter in g2:
            f1.add_arc('start', '2', (letter), (letter))
            f1.add_arc('start', '2', (letter.upper()), (letter.upper()))
            f1.add_arc('2', '2', (letter), ())
            for i in ['1','7','3','4','5','6']:
                f1.add_arc(i, '2', (letter), ('2'))
        elif letter in g3:
            f1.add_arc('start', '3', (letter), (letter))
            f1.add_arc('start', '3', (letter.upper()), (letter.upper()))
            f1.add_arc('3', '3', (letter), ())
            for i in ['1','2','7','4','5','6']:
                f1.add_arc(i, '3', (letter), ('3'))
        elif letter in g4:
            f1.add_arc('start', '4', (letter), (letter))
            f1.add_arc('start', '4', (letter.upper()), (letter.upper()))
            f1.add_arc('4', '4', (letter), ())
            for i in ['1','2','3','7','5','6']:
                f1.add_arc(i, '4', (letter), ('4'))
        elif letter in g5:
            f1.add_arc('start', '5', (letter), (letter))
            f1.add_arc('start', '5', (letter.upper()), (letter.upper()))
            f1.add_arc('5', '5', (letter), ())
            for i in ['1','2','3','4','7','6']:
                f1.add_arc(i, '5', (letter), ('5'))
        elif letter in g6:
            f1.add_arc('start', '6', (letter), (letter))
            f1.add_arc('start', '6', (letter.upper()), (letter.upper()))
            f1.add_arc('6', '6', (letter), ())
            for i in ['1','2','3','4','5','7']:
                f1.add_arc(i, '6', (letter), ('6'))
    return f1

    # The stub code above converts all letters except the first into '0'.
    # How can you change it to do the right conversion?

def truncate_to_three_digits():
    """
    Create an FST that will truncate a soundex string to three digits
    """

    # Ok so now let's do the second FST, the one that will truncate
    # the number of digits to 3
    f2 = FST('soundex-truncate')

    # Indicate initial and final states
    f2.add_state('start')
    f2.add_state('1')
    f2.add_state('2')
    f2.add_state('3')
    
    f2.initial_state = 'start'
    
    f2.set_final('1')
    f2.set_final('2')
    f2.set_final('3')

    # Add the arcs
    for letter in string.letters:
        f2.add_arc('start', 'start', (letter), (letter))

    for n in range(0,10):
        f2.add_arc('start', '1', (str(n)), (str(n)))
        f2.add_arc('1', '2', (str(n)), (str(n)))
        f2.add_arc('2', '3', (str(n)), (str(n)))
        f2.add_arc('3', '3', (str(n)), ())

    return f2

    # The above stub code doesn't do any truncating at all -- it passes letter and number input through
    # what changes would make it truncate digits to 3?

def add_zero_padding():
    # Now, the third fst - the zero-padding fst
    f3 = FST('soundex-padzero')

    f3.add_state('1')
    f3.add_state('2')
    f3.add_state('3')
    f3.add_state('4')
    
    f3.initial_state = '1'
    f3.set_final('4')

    f3.add_arc('1', '4', (), ('000'))
    f3.add_arc('2', '4', (), ('00'))
    f3.add_arc('3', '4', (), ('0'))

    for letter in string.letters:
        f3.add_arc('1', '1', (letter), (letter))
    for number in range(0,10):
        f3.add_arc('1', '2', (str(number)), (str(number)))
        f3.add_arc('2', '3', (str(number)), (str(number)))
        f3.add_arc('3', '4', (str(number)), (str(number)))
    
##    f3.add_arc('1', '4', (), ('000'))
##    f3.add_arc('2', '4', (), ('00'))
##    f3.add_arc('3', '4', (), ('0'))
    return f3

    # The above code adds zeroes but doesn't have any padding logic. Add some!

if __name__ == '__main__':
    user_input = raw_input().strip()
    f1 = letters_to_numbers()
    f2 = truncate_to_three_digits()
    f3 = add_zero_padding()

    if user_input:
        print("%s -> %s" % (user_input, composechars(tuple(user_input), f1, f2, f3)))
