import logging
import random
import re
from collections import namedtuple

# Fix Python2/Python3 incompatibility
# try: input = raw_input
# except NameError: pass

log = logging.getLogger(__name__)


class Key:
    def __init__(self, word, weight, decomps):
        self.word = word
        self.weight = weight
        self.decomps = decomps


class Decomp:
    def __init__(self, parts, save, reasmbs):
        self.parts = parts
        self.save = save
        self.reasmbs = reasmbs
        self.next_reasmb_index = 0


class Eliza:
    def __init__(self):
        self.initials = []
        self.finals = []
        self.quits = []
        # preprocessing
        # this 'pres' dictionary is used to preprocess the user's input before it is processed by the chatbot. Specifically, if the user's input contains any of the keys in pres, the chatbot will replace the key with its corresponding value in pres. This can be useful for normalizing variations of certain words, such as replacing "dont" with "don't"
        self.pres = {}
        # this 'posts' dictionary contains keys and values that are used to replace certain words or phrases in the chatbot's output before it is presented to the user
        self.posts = {}
        self.synons = {}
        self.keys = {}
        self.memory = []

    def load(self, path):
        key = None
        decomp = None
        with open(path) as file:
            # read each line in text file
            for line in file:
                # strip() return a string with all leading and trailing whitespace characters removed
                # If the resulting string is empty, which means the original line contained only whitespace characters or was an empty line
                if not line.strip():
                    continue
                # extract tag (before the ':') and content
                tag, content = [part.strip() for part in line.split(':')]
                if tag == 'initial':
                    self.initials.append(content)
                elif tag == 'final':
                    self.finals.append(content)
                elif tag == 'quit':
                    self.quits.append(content)
                elif tag == 'pre':
                    # the content of the line is split into parts using whitespace as a delimiter. The first part is treated as the key and the rest of the parts are added to the pres dictionary as the value associated with that key.
                    parts = content.split(' ')
                    self.pres[parts[0]] = parts[1:]
                elif tag == 'post':
                    parts = content.split(' ')
                    self.posts[parts[0]] = parts[1:]
                elif tag == 'synon':
                    parts = content.split(' ')
                    self.synons[parts[0]] = parts
                elif tag == 'key':
                    # examples
                    # key: apologise
                    # -> the word is 'apologies' and the weight is 1
                    # key: remember 5
                    # -> the word is 'remember' and the weight is 5
                    parts = content.split(' ')
                    word = parts[0]
                    weight = int(parts[1]) if len(parts) > 1 else 1
                    key = Key(word, weight, [])
                    self.keys[word] = key
                elif tag == 'decomp':
                    # example
                    # 1. '* i remember *' -> parts = ['*', 'i', 'remember', '*']
                    # 2. '* i @desire *' -> parts = ['*', 'i', '@desire', '*']
                    # 3. '* i am * @sad *' -> parts = ['*', 'i', 'am', '*', '@sad', '*']
                    # 4. '$ * my *' -> parts = ['$', '*', 'my', '*']
                    parts = content.split(' ')
                    save = False
                    # this '$' sign will check if save = True
                    if parts[0] == '$':
                        save = True
                        # 4. parts = ['*', 'my', '*']
                        parts = parts[1:]
                    decomp = Decomp(parts, save, [])
                    key.decomps.append(decomp)
                elif tag == 'reasmb':
                    # content: 'What else do you recollect ?' -> parts = ['What', 'else', 'do', 'you', 'recollect', '?']
                    # content: 'Why do you recollect (2) just now ?' -> parts = ['Why', 'do', 'you', 'recollect' , '(2)', 'just', 'now']
                    parts = content.split(' ')
                    decomp.reasmbs.append(parts)

    # a recursive function that is used to match a given input phrase (as a list of words) with a decomposition pattern (as a list of pattern parts) in order to determine the appropriate response for the given input
    def _match_decomp_r(self, parts, words, results):
        if not parts and not words:
            return True
        if not parts or (not words and parts != ['*']):
            return False
        if parts[0] == '*':
            for index in range(len(words), -1, -1):
                results.append(words[:index])
                if self._match_decomp_r(parts[1:], words[index:], results):
                    return True
                results.pop()
            return False
        elif parts[0].startswith('@'):
            root = parts[0][1:]
            if not root in self.synons:
                raise ValueError("Unknown synonym root {}".format(root))
            if not words[0].lower() in self.synons[root]:
                return False
            results.append([words[0]])
            return self._match_decomp_r(parts[1:], words[1:], results)
        elif parts[0].lower() != words[0].lower():
            return False
        else:
            return self._match_decomp_r(parts[1:], words[1:], results)

    def _match_decomp(self, parts, words):
        results = []
        if self._match_decomp_r(parts, words, results):
            return results
        return None

    def _next_reasmb(self, decomp):
        index = decomp.next_reasmb_index
        result = decomp.reasmbs[index % len(decomp.reasmbs)]
        decomp.next_reasmb_index = index + 1
        return result

    def _reassemble(self, reasmb, results):
        output = []
        for reword in reasmb:
            if not reword:
                continue
            if reword[0] == '(' and reword[-1] == ')':
                index = int(reword[1:-1])
                if index < 1 or index > len(results):
                    raise ValueError("Invalid result index {}".format(index))
                insert = results[index - 1]
                for punct in [',', '.', ';']:
                    if punct in insert:
                        insert = insert[:insert.index(punct)]
                output.extend(insert)
            else:
                output.append(reword)
        return output

    # substitute word with pres or synonyms
    # words: ['cant', 'believe']
    # self.pres (sub): {'cant': ['cannot'], 'believe': ['think']}
    # return ['cannot', 'think']
    def _sub(self, words, sub):
        output = []
        for word in words:
            word_lower = word.lower()
            if word_lower in sub:
                output.extend(sub[word_lower])
            else:
                output.append(word)
        return output

    def _match_key(self, words, key):
        for decomp in key.decomps:
            results = self._match_decomp(decomp.parts, words)
            if results is None:
                log.debug('Decomp did not match: %s', decomp.parts)
                continue
            log.debug('Decomp matched: %s', decomp.parts)
            log.debug('Decomp results: %s', results)
            results = [self._sub(words, self.posts) for words in results]
            log.debug('Decomp results after posts: %s', results)
            reasmb = self._next_reasmb(decomp)
            log.debug('Using reassembly: %s', reasmb)
            if reasmb[0] == 'goto':
                goto_key = reasmb[1]
                if not goto_key in self.keys:
                    raise ValueError("Invalid goto key {}".format(goto_key))
                log.debug('Goto key: %s', goto_key)
                return self._match_key(words, self.keys[goto_key])
            output = self._reassemble(reasmb, results)
            if decomp.save:
                self.memory.append(output)
                log.debug('Saved to memory: %s', output)
                continue
            return output
        return None

    def respond(self, text):
        if text.lower() in self.quits:
            return None

        # \s : space character ' '
        # * : appears 0 or n times
        # \. : the '.' character
        # + : appears 1 or n times
        # this mean any substring with <0_to_n_spaces><1_to_n_dots><0_to_n_spaces> will be replaced with ' . ' (space then dot then space)
        # "This ... is some text   .. .with many dots...." -> "This . is some text .  . with many dots . "
        text = re.sub(r'\s*\.+\s*', ' . ', text)
        # ,+ : ',' appears 1 or n times
        # <0_to_n_spaces><1_to_n_commas><0_to_n_spaces> will be replaced with ' , ' (space then comma then space)
        # "This ,,, is some text   ,,with many commas ,,  , ,." -> 'This , is some text , with many commas ,  ,  , .'
        text = re.sub(r'\s*,+\s*', ' , ', text)
        text = re.sub(r'\s*;+\s*', ' ; ', text)
        # 'last  night  I dreamed  . about  teeny, frahoop'
        log.debug('After punctuation cleanup: %s', text)
        
        # this will truncate redundant spaces
        words = [w for w in text.split(' ') if w]
        # ['last', 'night', 'I', 'dreamed', '.', 'about', 'teeny', ',', 'frahoop']
        log.debug('Input: %s', words)

        # subtitute words with preprocessing words
        words = self._sub(words, self.pres)
        log.debug('After pre-substitution: %s', words)

        keys = [self.keys[w.lower()] for w in words if w.lower() in self.keys]
        keys = sorted(keys, key=lambda k: -k.weight)
        log.debug('Sorted keys: %s', [(k.word, k.weight) for k in keys])

        output = None

        for key in keys:
            output = self._match_key(words, key)
            if output:
                log.debug('Output from key: %s', output)
                break
        if not output:
            if self.memory:
                index = random.randrange(len(self.memory))
                output = self.memory.pop(index)
                log.debug('Output from memory: %s', output)
            else:
                output = self._next_reasmb(self.keys['xnone'].decomps[0])
                log.debug('Output from xnone: %s', output)

        return " ".join(output)

    def initial(self):
        return random.choice(self.initials)

    def final(self):
        return random.choice(self.finals)

    def run(self):
        print(self.initial())

        while True:
            sent = input('> ')

            output = self.respond(sent)
            if output is None:
                break

            print(output)

        print(self.final())


def main():
    eliza = Eliza()
    eliza.load('doctor.txt')
    eliza.run()

if __name__ == '__main__':
    logging.basicConfig()
    main()
