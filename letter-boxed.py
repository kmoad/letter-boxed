from collections import defaultdict

words = set()
with open('words.txt') as f:
    for l in f:
        words.add(l.strip())

class PrefixNode(object):
    def __init__(self, parent=None):
        self.children = {}
        self.parent = parent
        self.word = None
        # self.letter = None

    def add(self, word, n=0):
        # if n>0:
        #     self.letter = word[n-1]
        if n == len(word):
            self.word = word
        else:
            next_n = n+1
            next_letter = word[n]
            if next_letter not in self.children:
                self.children[next_letter] = PrefixNode(parent=self)
            self.children[next_letter].add(word, n=next_n)
    
    # def __getitem__(self, letter):
    #     return self.children[letter]
    
    # def __iter__(self):
    #     for child in self.children.values():
    #         yield child

    # def check(self, prefix, leaf=False):
    #     if len(prefix) == 1:
    #         if leaf:
    #             return self.word is not None and self.word[-1] == prefix
    #         else:
    #             return prefix in self.children
    #     else:
    #         if prefix[0] in self.children:
    #             return self.children[prefix[0]].check(prefix[1:], leaf=leaf)
    #         else:
    #             return False

    # def count(self):
    #     cnt = 1 if self.word else 0
    #     return cnt + sum([_.count() for _ in self.children.values()])

    def lb_iter(self, letter_box, last_group=None):
        words = []
        if self.word:
            words.append(self.word)
        for next_letter, child in self.children.items():
            can_continue, this_group = letter_box.check_letter(next_letter, last_group = last_group)
            if can_continue:
                words += child.lb_iter(letter_box, last_group=this_group)
        return words
        

class LetterBox(object):
    def __init__(self, sides):
        self.sides = sides
        self.all_letters = set()
        for side in sides:
            self.all_letters |= set(''.join(side))

    def check_letter(self, letter, last_group=None):
        for group_id, letters in enumerate(self.sides):
            if letter not in letters:
                continue
            if group_id == last_group:
                return False, None
            else:
                return True, group_id
        return False, None
    
    def check_coverage(self, words):
        query_letters = set(''.join(words))
        return query_letters == self.all_letters

# 2022-05-26
lb = LetterBox([
    ['N','E','P'],
    ['U','L','A'],
    ['B','D','T'],
    ['I','C','M'],
])
# 2022-05-25
# lb = LetterBox([
#     ['D','T','E'],
#     ['C','R','V'],
#     ['A','O','Y'],
#     ['I','H','L'],
# ])
# https://medium.com/@pnmclaugh/solving-letter-boxed-in-python-5e6cc4b216f9
# lb = LetterBox([
#     ['S','M','A'],
#     ['I','L','P'],
#     ['T','N','E'],
#     ['O','C','Z'],
# ])
# print(lb.all_letters)

tree = PrefixNode()
for word in words:
    tree.add(word)

valid_words = [_ for _ in tree.lb_iter(lb) if len(_)>2]
# print(len(valid_words))
valid_words.sort(key=lambda _: len(_), reverse=True)
# print(valid_words)
words_by_start = defaultdict(list)
for word in valid_words:
    words_by_start[word[0]].append(word)

# This is a combinatorial problem. Work should be done to reduce the difficulty.
# But it will be impossible to avoid the O(n^k) complexity completely. Thankfully,
# n is at least somewhat bounded
def get_solution(valid_words, words_by_start, letter_box, prev_chain=[], max_length=5):
    solutions = []
    if prev_chain:
        cur_words = words_by_start[prev_chain[-1][-1]]
    else:
        cur_words = valid_words
    # Check for solution this iteration
    for word in cur_words:
        cur_chain = prev_chain + [word]
        if letter_box.check_coverage(cur_chain):
            # print(cur_chain)
            solutions.append(cur_chain)
    if solutions:
        return solutions
    # Fail if this iteration was last
    if len(prev_chain) == max_length-1:
        return []
    # Check next iteration
    for word in cur_words:
        cur_chain = prev_chain + [word]
        next_solutions = get_solution(valid_words, words_by_start, letter_box, prev_chain=cur_chain, max_length=max_length)
        if next_solutions:
            solutions += next_solutions
    return solutions
    # return []

solutions = get_solution(valid_words, words_by_start, lb, max_length=2)
# print(len(solutions))
for solution in solutions:
    print('\t'.join(solution))