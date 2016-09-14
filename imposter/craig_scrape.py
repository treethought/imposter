from bs4 import BeautifulSoup as bs
import requests
import timeit
from config import *


class CraigScraper(object):

    def __init__(self, city='newyork', category='mis', **kwargs):
        self.__dict__.update(kwargs)
        self.city = city
        self.category= category
        self.base_url = 'https://{}.craigslist.org'.format(self.city)
        self.search_url = '{}/{}'.format(self.base_url, self.category)
        self.session = requests.Session()
        self.post_results = {}
        self.body_file = os.path.join(CORPUS_FILES_DIR, '{}_{}.txt'.format(self.city, self.category))
        self.url_file = os.path.join(SCRAPED_URLS_DIR, '{}_{}_urls.txt'.format(self.city, self.category))
        # self.body_file = '/Users/Cam/projects/markbot/markbot/imposter/bot_files/{}_body.txt'.format(self.category)
        # self.url_file = '/Users/Cam/projects/markbot/imposter/bot_files/{}_urls.txt'.format(self.category)

        def __repr__(self):
            return self.file

    def get_soup(self, url):
        page = self.session.get(url)
        page.encoding = 'UTF-8'
        return bs(page.text, 'html.parser')

    def get_page_urls(self, search_url):
        """Yields post urls from current result page"""
        soup = self.get_soup(search_url)
        posts = soup.select('p > span.txt')
        for post in posts:
            link = post('a')[0]
            url = self.base_url + link['href']
            yield url
            

    def all_post_urls(self, search_url):
        """yields generated list of post urls by navigating through result pages"""
        soup = self.get_soup(search_url)
        next_page = search_url
        post_urls = []
        while next_page:
            for url in self.get_page_urls(next_page):
                yield url
            next_page = self.base_url + soup.select('span.buttons > a.button.next')[0]['href']

    def scrape_body(self, post_url):
        """Returns body of post as a string"""
        soup = self.get_soup(post_url)
        try:
            body = soup.select('#postingbody')[0].text
            return body.strip()
        except IndexError:
            if soup.select('#userbody > div.removed'):
                return('')






    # def get_content(self, post_url):
    #     """Returns a tuple containing title, body, id"""
    #     soup = self.get_soup(post_url)
    #     try:
    #         title = post_soup.select('#titletextonly')[0].text
    #         body = post_soup.select('#postingbody')[0].text
    #         post_info = post_soup.select('p.postinginfo')
    #         post_id = post_info[1].text.split(': ')[1]
    #         return post_id, title, body
    #     except IndexError:
    #         if post_soup.select('#userbody > div.removed'):
    #             print('Flagged for removal')



    # def get_info(self, post_soup):
    #     """Returns dictionary of attributes, with Post fields as keys"""
    #     attributes = {}
    #     try:
    #         atts = post_soup.select('div.mapAndAttrs')[0]
    #     except IndexError:
    #         print('no atts')
    #     else:
    #         details = atts.select('p.attrgroup')
    #         for d in details:
    #             info = d('span')[0].text.split(': ')
    #             attribute = info[0]
    #             value = info[1]
    #             attributes[attribute] = value
    #         try:
    #             gmap = atts.select('p > small > a')[0]
    #             attributes['gmap'] = gmap
    #         except IndexError as e:
    #             print('no map')
    #
    #
    #     post_info = post_soup.select('p.postinginfo')
    #
    #     attributes['post_id'] = post_info[1].text.split(': ')[1]
    #     datetime_split = post_info[2].text.split(' ')
    #     attributes['date'] = datetime_split[1]
    #     attributes['time'] = datetime_split[3]
    #
    #     return attributes




    # def run(self):
    #     start = timeit.default_timer()
    #     for url_set in self.all_post_urls(self.search_url):
    #         for url in url_set:
    #             soup = self.get_soup(url)
    #             post_data = self.get_content(soup)
    #             (post_data[2])
    #     end = timeit.default_timer()
    #     print('method 1 took {} sec'.format(end-start))

    def scrape_post_urls(self):  # works
        start = timeit.default_timer()

        urls = self.all_post_urls(self.search_url)
        for url in urls:
            print(url)
            with open(self.url_file, 'a+') as f:
                f.write(url + '\n')

            # soup = self.get_soup(url)
            # post_data = self.get_content(soup)
            # (post_data[2])
        end = timeit.default_timer()
        print('method 2 took {} sec'.format(end-start))

    def write_bodies(self):
        start = timeit.default_timer()
        with open(self.url_file, 'r') as url_file:
            with open(self.body_file, 'a') as body_file:
                for url in url_file.readlines():
                # for url in urls:
                    body = self.scrape_body(url.strip())
                    body_file.write(body)
                    print('wrote')
        end = timeit.default_timer()
        print('method 2 took {} sec'.format(end-start))






client = CraigScraper()
# client.scrape_post_urls()
client.write_bodies()


