import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPOSTER_DIR = os.path.join(PROJECT_ROOT, 'imposter')
RESOURCES = os.path.join(PROJECT_ROOT, 'resources')
CORPUS_FILES_DIR = os.path.join(RESOURCES, 'corpus_files')
BOTS_DIR = os.path.join(IMPOSTER_DIR, 'bots')
LYRICS_DIR = os.path.join(CORPUS_FILES_DIR, 'lyrics')

SCRAPED_URLS_DIR = os.path.join(PROJECT_ROOT, 'scraped_urls')

