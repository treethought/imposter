import itertools
import json
import random
import shutil
from ast import literal_eval

import frogress

from config import *


class Imposter(object):

    def __init__(self, corpus_file):

        self.file = corpus_file
        self.cache = {}
        self.word_count = 0
        self.create_directory()
        self._build_cache()

    def __repr__(self):
        return self.name

    @property
    def name(self):
        path = self.file.split('.txt')[0]
        return path.split('/')[-1]

    def create_directory(self):
        self.bot_dir = os.path.join(BOTS_DIR, self.name)
        os.makedirs(self.bot_dir, exist_ok=True)

        self.corpus_file = os.path.join(self.bot_dir, 'corpus.txt')
        open(self.corpus_file, 'a').close()

        #copy input file to bot directory
        shutil.copyfile(self.file, self.corpus_file)


    @property
    def cache_file(self):
        path = os.path.join(self.bot_dir, 'cache.json')
        if not os.path.isfile(path):
            open(path, 'a').close()
        return path                 #TODO return file handler instead of path, to skip opening in other methods

    @property
    def result_file(self):
        path = os.path.join(self.bot_dir, 'results.txt')
        return path

    def add_to_corpus(self, text):
        """Text may be a string of text or filepath. Content is added to corpus file,
            and becomes accessible with self.words"""
        if os.path.isfile(text):
            self.add_file_to_corpus(text)
        else:
            self.add_text_to_corpus(text)

    def add_text_to_corpus(self, string):
        with open(self.corpus_file, 'a') as f:
            f.write('\n' + string + '\n')
        self._rebuild_cache()

    def add_file_to_corpus(self, path):
        with open(self.corpus_file, 'a') as corpus:
            with open(path, 'r') as f:
                for line in f.readlines():
                    corpus.write(line)
        self._rebuild_cache()

    @property
    def words(self):
        self.word_count = 0
        with open(self.corpus_file) as f:
            for line in f.readlines():
                for word in line.split():
                    self.word_count += 1
                    yield word

    @property
    def raw_states(self, order=6):
        steps = []
        for i in range(order):
            steps.append(itertools.islice(self.words, i, None))
        yield from zip(*steps)


    @property
    def processed_states(self):
        for state in self.raw_states:
            for word in state:
                if word[-1] in '.?!':
                    end_pos = state.index(word)
                    state = state[:end_pos+1]
                    break
            print(state)



    def _save_cache(self):
        """Writes cache dictionary to json file.
            Always overwrites file, so must load and update data before saving updates.
            Cache keys converted from tuple -> str for json
        """
        print('saving data')
        with open(self.cache_file, 'w') as f:
            data = {str(k): v for k, v in self.cache.items()}  # convert tuple key into string for json
            json.dump(data, f, indent=2)
    @property
    def data(self):
        """Opens and loads JSON data into memory, does not add to cache
            Returns None if no data found"""
        try:
            with open(self.cache_file, 'r+') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError:
            print('no data found')
            return None

    def _build_cache(self):
        """Builds cache from json, if data previously saved.
            Otherwise builds cache by generating states from corpus
        """
        print('Building cache...')
        assert self.cache == {}
        if self.data:
            print('loading data from json')
            self.load_saved_cache()
        else:
            print('from states')
            self._build_cache_from_corpus()
        self._save_cache()

    def _build_cache_from_corpus(self):
        """Parses states from corpus file and loads them into cache"""
        print('Populating cache with word_states')
        try:
            for state in frogress.bar(self.raw_states):
                key = (state[0], state[1])
                if key in self.cache:
                    self.cache[key].append(state[2])
                else:
                    self.cache[key] = [state[2]]  # values are list of words
        except KeyboardInterrupt:
            print('Saving data and quiting')
        finally:
            self._save_cache()

    def load_saved_cache(self):
        """Loads saved states data from json into cache.
            Doesn't overwrite cache item if in-memory item has larger value"""
        if self.data:
            for k, v in self.data.items():
                key = literal_eval(k)
                if key in self.cache.keys():
                    if len(v) <= len(self.cache[key]):
                        continue
                self.cache[key] = v
        return self.cache

    def _rebuild_cache(self):
        """Builds cache only from corpus, cache is then saved to update json"""
        self.cache = {}
        self._build_cache_from_corpus()

    def select_seed(self):
        seed_idx = random.randint(0, len(self.cache) - 3)
        seed_words = itertools.islice(self.words, seed_idx, seed_idx + 2)
        return(tuple(seed_words))

    def generate_text(self, size=139, min_size=20):  #FOR ENDING WITH END OF SENTENCE
        new_word, next_word = self.select_seed()
        new_word[0].upper()
        result = []
        for i in range(size):
            result.append(new_word)
            if new_word[-1] in '.?!' and i > min_size:
                break
            if len(result) == 140:
                break
            new_word, next_word = next_word, random.choice(self.cache[(new_word, next_word)])

        # result.append(next_word)
        result = ' '.join(result)

        self.write_result(result)
        return result


    def write_result(self, result):
        with open(self.result_file, 'a+') as f:
            f.write('{}\n\n'.format(result))



if __name__ == '__main__':
    b = Imposter(os.path.join(CORPUS_FILES_DIR, 'shakespeare.txt'))
    print(b.generate_text(size=100))




