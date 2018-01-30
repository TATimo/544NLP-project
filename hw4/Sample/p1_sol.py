# Rosalyn Tan
# Code to learn a probabilistic CFG from trees

from Queue import PriorityQueue
from tree import Tree

rules = {}
prob = {}

def read_trees():
	for line in open("./train.trees.pre.unk"):
		t = Tree.from_str(line)
		for node in t.bottomup():
			if node.children == []:
				continue
			right = ''
			for child in node.children:
				right = right + ' ' + child.label
			if node.label not in rules:
				rules[node.label] = {}
			if right in rules[node.label]:
				rules[node.label][right] += 1
			else:
				rules[node.label][right] = 1

def count_rules():
	q = PriorityQueue()
	unique_rules = 0
	for rule in rules:
		for right in rules[rule]:
			unique_rules += 1
			q.put((-rules[rule][right], rule + ' ->' + right))

	print('Number of unique rules: %d' % unique_rules)
	print('Top 5 most frequent rules:')
	for i in range(0, 5):
		freq = q.get()
		print(str(freq[1]) + ' # ' + str(freq[0]*-1))

def cond_prob():
	q = PriorityQueue()
	left_count = 0
	for rule in rules:
		prob[rule] = {}
		for right in rules[rule]:
			left_count += rules[rule][right]
		for right in rules[rule]:
			prob[rule][right] = rules[rule][right] / left_count
			q.put((-prob[rule][right], rule + ' ->' + right))
#			print(rule + ' ->' + right + ' # ' + str(prob[rule][right]))
		left_count = 0
	
	print('Top 5 highest probability rules:')
	for i in range(0, 5):
		p = q.get()
		print(str(p[1]) + ' # ' + str(p[0]*-1))

if __name__ == '__main__':
	read_trees()
	count_rules()
	cond_prob()
