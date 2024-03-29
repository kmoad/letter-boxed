from collections import defaultdict

class PrefixTree(object):
    def __init__(self, words):
        self.prefix = ''
        self.is_word = False
        self.children = defaultdict(lambda: self.__class__([]))
        for word in words:
            self.add(word, n=0)

    def add(self, word, n=0):
        self.prefix = word[:n]
        if self.prefix == word:
            self.is_word = True
        else:
            self.children[word[n]].add(word, n=n+1)
    
    def __getitem__(self, prefix):
        if prefix[0] in self.children:
            if len(prefix) <= 1:
                return self.children[prefix[0]]
            else:
                return self.children[prefix[0]][prefix[1:]]
        else:
            raise KeyError(prefix)
    
    def __contains__(self, prefix):
        if len(prefix) <= 1:
            return prefix in self.children
        else:
            return prefix[1:] in self.children[prefix[0]]

    def get(self, *args):
        try:
            self[args[0]]
        except KeyError:
            return args[1] if len(args)>=2 else None

    def __iter__(self):
        if self.is_word:
            yield self
        for child in self.children.values():
            yield from child

    def __len__(self):
        n = int(self.is_word)
        return n + sum([len(_) for _ in self.children.values()])

    def lb_iter(self, letter_box, last_side=None):
        if self.is_word:
            yield self.prefix
        cur_side = last_side
        for next_letter, child in self.children.items():
            can_continue, cur_side = letter_box.check_letter(next_letter, exclude_side = last_side)
            if can_continue:
                yield from child.lb_iter(letter_box, last_side=cur_side)

class LetterBox(object):
    def __init__(self, sides):
        self.sides = [list(_) for _ in sides]
        self.all_letters = set()
        for side in self.sides:
            self.all_letters |= set(side)

    def check_letter(self, query_letter, exclude_side=None):
        for side_index, side_letters in enumerate(self.sides):
            if query_letter in side_letters:
                if side_index != exclude_side:
                    return True, side_index
                else:
                    return False, None
        return False, None

    def check_coverage(self, words):
        return set(''.join(words)) == self.all_letters

# This is a combinatorial problem. Work should be done to reduce the difficulty.
# But it will be impossible to avoid the O(n^k) complexity completely. Thankfully,
# n is bounded.
def get_solutions(words, words_by_start, letter_box, prev_chain=[], max_length=5):
    if prev_chain:
        cur_words = words_by_start[prev_chain[-1][-1]]
    else:
        cur_words = words
    # Check for solution this layer
    for word in cur_words:
        cur_chain = prev_chain + [word]
        if letter_box.check_coverage(cur_chain):
            yield cur_chain
    # Fail if this layer was the last
    if len(prev_chain) == max_length-1:
        return
    # Check next layer
    for word in cur_words:
        if word in cur_chain:
            continue
        cur_chain = prev_chain + [word]
        # Skip next layer if this layer solves
        if letter_box.check_coverage(cur_chain):
            continue
        yield from get_solutions(words, words_by_start, letter_box, prev_chain=cur_chain, max_length=max_length)

if __name__ == '__main__':
    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser()
    parser.add_argument('letters',
        help='Format: ABC-DEF-GHI-JKL',
    )
    parser.add_argument('-l', '--length', dest='max_length',
        type=int,
        default=2,
        help='Max solution length. Default: 2',
    )
    parser.add_argument('--min-word-length', dest='min_word_length',
        type=int,
        default=2,
        help='Minimum word length',
    )
    parser.add_argument('--max-word-length', dest='max_word_length',
        type=int,
        default=None,
        help='Minimum word length',
    )
    parser.add_argument('-w', '--words', dest='words_fp',
        type=Path,
        default=Path('words_easy.txt'),
        help='File containing words. Default: words_easy.txt',
    )
    parser.add_argument('--box-words',
        action='store_true',
        help='Output just the words that fit the box'
    )
    args = parser.parse_args()

    all_words = args.words_fp.read_text().split()
    if args.min_word_length:
        tmp = [_ for _ in all_words if len(_) >= args.min_word_length]
        all_words = tmp
        del tmp
    if args.max_word_length:
        tmp = [_ for _ in all_words if len(_) <= args.max_word_length]
        all_words = tmp
        del tmp
    all_words.sort()
    prefix_tree = PrefixTree(all_words)

    letter_box = LetterBox(args.letters.upper().split('-'))

    box_words = list(prefix_tree.lb_iter(letter_box))
    box_words.sort(key=len, reverse=True)
    
    if args.box_words:
        print('\n'.join(box_words))
        exit()

    by_start = defaultdict(list)
    for word in box_words:
        by_start[word[0]].append(word)
    
    for solution in get_solutions(box_words, by_start, letter_box, max_length=args.max_length):
        print(' '.join(solution))
