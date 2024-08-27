# This word list is sourced from http://wordlist.aspell.net/12dicts/
# using 12dicts-6.0.2/International/3of6game.txt with some preprocessing
# to remove any annotations.
WORD_LIST = '12dicts_words'

# Change this to the length of word you'd like to try.
MIN_WORD_LEN = 3
MAX_WORD_LEN = 5

# Maximum depth to compute a search. Shouldn't ever need to be higher,
# but you may lower it to quit early in a very large dictionary.
MAX_ITERS = 100

from collections import defaultdict

ORD_BEFORE_A = ord("A") - 1

# Convert a string to a number
def make_number(word):
    num = 0
    mult = 1
    for w in word:
        num += (ord(w) - ORD_BEFORE_A) * mult
        mult *= 256
    return num

# Convert a number to a string
def make_word(number):
    word = ""
    while number:
        word += chr((number & 0xFF) + ORD_BEFORE_A)
        number >>= 8
    return word

# Check if 2 strings differ by only 1 letter (slow)
def are_pair(w1, w2):
    numDiffs = 0
    for i in range(len(w1)):
        if w1[i] != w2[i]:
            numDiffs += 1
            if numDiffs >= 2: return False
    return numDiffs == 1


# Check if 2 numbers differ by only 1 letter (fast)
def are_pair_num(n1, n2):
    numDiffs = 0
    for i in range(WORD_LEN):
        if ((n1 >> (i*8)) & 0xFF) != ((n2 >> (i*8)) & 0xFF):
            numDiffs += 1
            if numDiffs >= 2: return False
    return numDiffs == 1

# Returns all possible short word (which may or may not be words)
def shorter_nums(n1, length):
    # Remove a letter at a time, result of the first 3 loops are:
    # w1 >> 8
    # w1 >> 16 << 8 + (w1 & (2**8-1))
    # w1 >> 24 << 16 + (w1 & (2**16-1))
    maybes = [(n1 >> (8 * (slot + 1)) << (8 * slot)) + (n1 & (256 ** slot - 1)) for slot in range(length)]
    return [n for n in maybes if n in all_words_by_len[length - 1]]

# Create a lookup table for 1 letter diffs (fastest)
print('Creating Diff Lookup Table...')
pair_lut = set()
for i in range(MAX_WORD_LEN):
    for j in range(32):
        pair_lut.add(j << (i * 8))

print('Loading Dictionary...')
all_words = []
all_words_by_len = {}

short_to_longer_words = defaultdict(lambda : [])

# We want empty arrays when going out of bound
for i in range(MAX_WORD_LEN + 2):
    all_words_by_len[i] = []
all_words_by_len[-1] = []

with open(WORD_LIST + '.txt', 'r') as fin:
    for word in fin:
        word = word.strip().upper()
        if MIN_WORD_LEN <= len(word) <= MAX_WORD_LEN:
            number = make_number(word)
            all_words.append(number)
            all_words_by_len[len(word)].append(number)
            for shorter_num in shorter_nums(number, len(word)):
                short_to_longer_words[shorter_num].append(number)

print('Loaded ' + str(len(all_words)) + ' words.')

print('Finding All Connections...') # Only for the graph
all_pairs = []
for w1_len in range(MIN_WORD_LEN, MAX_WORD_LEN + 1):
    w1_all_words = all_words_by_len[w1_len]
    for i in range(len(w1_all_words)):
        w1 = w1_all_words[i]
        word1 = make_word(w1)
        # Same length matching
        for j in range(i):
            w2 = w1_all_words[j]
            #p = are_pair_num(w1, w2)
            p = (w1 ^ w2) in pair_lut
            if p:
                all_pairs.append((word1, make_word(w2)))

        # Shorter words matching
        for maybe_w in shorter_nums(w1, w1_len):
            if maybe_w in all_words_by_len[w1_len - 1]:
                all_pairs.append((word1, make_word(maybe_w)))

        # Longer words matching
        for maybe_w in short_to_longer_words[w1]:
            if maybe_w in all_words_by_len[w1_len + 1]:
                all_pairs.append((word1, make_word(maybe_w)))

print("Found " + str(len(all_pairs)) + " connections.")

# DOT file format does not allow these keywords, make sure to change them
keywords = ['NODE', 'EDGE', 'GRAPH', 'DIGRAPH', 'SUBGRAPH', 'STRICT']
def fix_keyword(w):
    if w in keywords:
        return '_' + w
    return w

print("Writing file...")
with open("graph.dot",'w') as fout:
    fout.write('graph words {\n')
    for w in all_words:
        word = fix_keyword(make_word(w))
        fout.write('  "' + word + '";\n')
    for w1,w2 in all_pairs:
        fout.write('  "' + fix_keyword(w1) + '" -- "' + fix_keyword(w2) + '";\n')
    fout.write('}\n')

# Main loop for solver interface
print("")
while True:
    from_word = make_number(input('From Word: ').upper())
    to_word = make_number(input('  To Word: ').upper())
    if from_word != 0 and not from_word in all_words:
        print("No connections to " + make_word(from_word))
        continue
    if not to_word in all_words:
        print("No connections to " + make_word(to_word))
        continue

    connections = {}
    dist = dict([(word,-1) for word in all_words])
    dist[to_word] = 0
    is_found = False
    for iter in range(MAX_ITERS):
        print(iter)
        made_changes = False

        for w1_len in range(MIN_WORD_LEN, MAX_WORD_LEN + 1):
            w1_all_words = all_words_by_len[w1_len]

            for w1 in w1_all_words:
                if dist[w1] == iter:
                    # Same length matching
                    for w2 in w1_all_words:
                        if dist[w2] != -1: continue
                        if (w1 ^ w2) not in pair_lut: continue
                        dist[w2] = iter + 1
                        connections[w2] = w1
                        made_changes = True
                        if w2 == from_word:
                            print("Found!")
                            is_found = True

                    # Shorter words matching
                    for w2 in shorter_nums(w1, w1_len):
                        if dist.get(w2) != -1: continue
                        # Would be better with a set
                        dist[w2] = iter + 1
                        connections[w2] = w1
                        made_changes = True
                        if w2 == from_word:
                            print("Found!")
                            is_found = True
                            break

                    # Longer words matching
                    for w2 in short_to_longer_words[w1]:
                        if dist[w2] != -1: continue
                        if w2 in all_words_by_len[w1_len + 1]:
                            # It's a real word, great!
                            dist[w2] = iter + 1
                            connections[w2] = w1
                            made_changes = True
                            if w2 == from_word:
                                print("Found!")
                                is_found = True
                                break

                if is_found: break
            if is_found: break
        if is_found or (not made_changes): break

    if from_word != 0:
        if not from_word in connections:
            print('Can not connect!')
        else:
            w = from_word
            while True:
                print(make_word(w))
                if w == to_word: break
                w = connections[w]
            print(str(dist[from_word]) + " steps")
    else:
        for word in all_words:
            if dist[word] > 0:
                print(make_word(word) + " in " + str(dist[word]) + " steps")
            #else:
            #    print(word + " no connection")
