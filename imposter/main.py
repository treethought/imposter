#! /usr/bin/env python
import random
import time
import tweepy

import markov
from config import *
from yikyakapi.yikyak import YikYak
from secrets import *

COUNTRY_CODE = 'USA'
SLO_COORDS = (35.296256, -120.665499)


def first_time_yak_auth():
    """Required for first authentication: Need to request and enter pin.
        In YikYak app, Me > Settings > Request Web Authentication"""
    print(first_time_yak_auth.__doc__)
    client = YikYak()
    pin = input("Web authentication PIN: ")
    client.login(COUNTRY_CODE, PHONE_NUMBER, pin)
    user_id = client.yakker.userID
    print('Save user_id in /imposter/secrets.py')
    print('user_id is: {}'.format(user_id))


def setup_yakker():
    yakker = YikYak()
    yakker.login_id(COUNTRY_CODE, PHONE_NUMBER, YAK_ID)
    return yakker


def setup_tweeter():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    tweeter = tweepy.API(auth)
    return tweeter


def main():
    yakker = setup_yakker()
    tweeter = setup_tweeter()
    bot = markov.Imposter(os.path.join(CORPUS_FILES_DIR, 'newyork_mis.txt'))
    while True:
        new_post = bot.generate_text()
        try:
            tweeter.update_status(new_post)
            yakker.compose_yak(new_post, *SLO_COORDS)
            print('posted -- {}'.format(new_post))
            time.sleep(random.randint(1800, 10800))
        except Exception as e:
            print(e)



if __name__ == '__main__':
    main()














