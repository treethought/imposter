import itertools
import random

from imposter.config import *
from imposter.markov import Imposter

CORPUS = os.path.join(CORPUS_FILES_DIR, 'testing.txt')
CACHE_FILE = os.path.join(BOTS_DIR, 'testing/cache.json')
NEW_CORP = os.path.join(CORPUS_FILES_DIR, 'tst_new_body.txt')

class TestMarkBot:

    def setup_method(self, method):
        assert os.path.isfile(CORPUS)
        assert not self.cache_file_exists()
        self.b = Imposter(CORPUS)
        self.b.cache_file
        assert self.cache_file_exists()

    def teardown_method(self, method):
        os.remove(CACHE_FILE)
        assert not self.cache_file_exists()
        self.b.cache = {}


    def cache_file_exists(self):
        return os.path.isfile(CACHE_FILE)

    def make_random_state_from_corpus(self):
        with open(self.b.corpus_file, 'r') as f:
            corpus = f.read().split()
            idx = random.randint(0, len(corpus) - 3)
            return (corpus[idx], corpus[idx + 1], corpus[idx + 2])

    def check_cache_matches_words(self):
        """Compares sequences in b.words and key-values in cache
        Cache must be built"""

        random_idx = random.randint(0, self.b.word_count - 7)

        state = list(itertools.islice(self.b.words, random_idx, random_idx + 3))
        state = self.make_random_state_from_corpus()
        key = tuple(state[:2])
        value = state[2]

        # assert type(self.b.cache[key]) is list
        assert isinstance(key, tuple)

        assert key in self.b.cache.keys()
        assert value in self.b.cache[key]

        # self.assertIs(self.b.cache[key][0], self.b.words[random_idx + 2]) #TODO
        # minus 6 bc last 2 raw_states  aren't yielded and so 6 (2 states * 3 words) dic elements missing
        # assert len(self.b.words) - 6 == len(self.b.cache)

    def test_words(self):
        with open(self.b.corpus_file) as f:
            corpus = f.read()
            count = 0
            for word in self.b.words:
                assert word is not None
                assert word in corpus
                count += 1
            assert self.b.word_count == count


    def test_raw_states(self):
        prev_word = []
        # assert self.b.raw_states is not None
        with open(self.b.corpus_file, 'r') as f:
            corpus = f.read().split()
            idx = random.randint(0, len(corpus)-3)
            random_triplet = (corpus[idx], corpus[idx+1], corpus[idx+2])
            assert random_triplet in self.b.raw_states

        for state in self.b.raw_states:
            assert state is not None
            assert len(state) == 3
            assert type(state) == tuple
            for word in state:
                assert word in self.b.words










    def save_sample_cache(self):
        sample_cache = {('kw1, kw2'): ['vw1']}
        self.b.cache = sample_cache
        self.b._save_cache()

    def change_in_file_size(self, func):
        pre_size = os.stat(self.b.cache_file).st_size
        func()
        post_size = os.stat(self.b.cache_file).st_size
        return post_size - pre_size

    def test__save_sample_cache(self):

        assert self.b.cache == {}
        change = self.change_in_file_size(self.save_sample_cache)
        assert change > 0


    def test_save_overwrites_file(self):
        """Saving the same data twice should make the file have
            the size of only one write
        """
        assert os.stat(self.b.cache_file).st_size == 0
        change = self.change_in_file_size(self.save_sample_cache)
        assert change > 0
        second_change = self.change_in_file_size(self.save_sample_cache)
        assert second_change == 0


    def test__load_data_from_saved_sample_cache(self):

        self.save_sample_cache()
        data = self.b.data
        assert data is not None
        assert data['kw1, kw2'] == ['vw1']
        for k, v in data.items():
            assert isinstance(k, str)  # json not vonerted in load data call, only when building cache
            assert len(k.split()) == 2
            assert isinstance(v, list)

    def test__build_cache_from_states(self):
        # assert len(self.b.cache) == 0
        self.b._build_cache_from_corpus()

        # assert self.b.cache[('hello', 'here')] == ['is']
        self.check_cache_matches_words()

    def test__build_cache_from_states_then_data(self):
        assert self.b.cache == {}
        self.b._build_cache_from_corpus()
        cache_from_text = self.b.cache
        self.b._save_cache()
        self.b.cache = {}
        self.b.load_saved_cache()
        assert self.b.cache == cache_from_text
        for k, v in self.b.cache.items():
            assert isinstance(k, tuple)  # json converted back to tuple
            assert len(k) == 2
            assert isinstance(v, list)


    def test__save_data_after_text_generated_cache(self):
        assert os.path.isfile(self.b.cache_file)
        change = self.change_in_file_size(self.b._build_cache_from_corpus)
        # change = self.change_in_file_size(self.b._save_data)
        assert change > 0


    def test_load_data_from_saved_text_generated_cache(self):
        self.b._build_cache_from_corpus()
        self.check_cache_matches_words()
        self.b._save_cache()
        # self.b.cache = {}
        data = self.b.data
        for k, v in data.items():
            assert isinstance(k, str)
            assert len(k.split()) == 2
            assert isinstance(v, list)

    def test_build_new_cache(self):
        assert self.b.cache == {}
        os.remove(CACHE_FILE)
        assert not os.path.isfile(CACHE_FILE)
        self.b._build_cache()
        assert os.path.isfile(CACHE_FILE)
        self.check_cache_matches_words()

    # def test_update_cache_with_new_sample_data(self):
    #     assert self.b.cache == {}
    #     self.b._build_cache_from_corpus()
    #     assert len(self.b.cache) > 4
    #     assert 'elephants' not in self.b.cache.values()
    #     self.b._save_data()
    #     file_size_after_save = os.stat(self.b.cache_file).st_size
    #
    #     self.b._update_cache_from_file('/Users/Cam/projects/markbot/imposter/bot_files/tst_new_body.txt')
    #     file_size_after_update = os.stat(self.b.cache_file).st_size
    #     assert file_size_after_update > file_size_after_save
    #     assert 'elephants' in self.b.cache.values()

    def test_add_to_corpus_from_string(self):
        try:
            new_text = 'There was no willy wonka in the hypodermic chamber that I saw. I injected my own owls'
            assert 'hypodermic' not in self.b.words
            self.b.add_to_corpus(new_text)
            self.b._rebuild_cache()

            with open(self.b.corpus_file, 'r') as f:
                assert new_text in f.read()

            # test that the updated corpus is correctly used to build cache
            assert 'hypodermic' in self.b.words
            assert ('hypodermic', 'chamber') in self.b.cache.keys()
            # assert ('')

            assert 'hypodermic' in self.b.cache[('in', 'the')]

        finally:
            #remove added words so future tests work
            with open(self.b.corpus_file, 'r') as f:
                rewrites = []
                for line in f.readlines():
                    if set(line.strip()) != set(new_text):
                        rewrites.append(line)
            with open(self.b.corpus_file, 'w') as f:
                f.writelines(rewrites)

    def test_add_to_corpus_from_file(self):
        with open(NEW_CORP, 'r') as f:
            content = f.read()
        # assert content.split() not in self.b.words
        self.b.add_to_corpus(NEW_CORP)
        with open(self.b.corpus_file, 'r') as f:
            assert content in f.read()

        for word in content.split():
            assert word in self.b.words

        self.b._rebuild_cache()

        # test cache was built correctly
        new_words = content.split()
        random_idx = random.randint(0, len(new_words)-6)
        random_key = (new_words[random_idx], new_words[random_idx+1])
        value = new_words[random_idx+2]

        assert random_key in self.b.cache.keys()
        assert value in self.b.cache[random_key]

        # remove added words so future tests work
        with open(self.b.corpus_file, 'r') as f:
            rewrites = []
            for line in f.readlines():
                if set(line.strip()) != set(content):
                    rewrites.append(line)
        with open(self.b.corpus_file, 'w') as f:
            f.writelines(rewrites)

        with open(self.b.corpus_file, 'r') as f:
            assert content not in f.read()














































