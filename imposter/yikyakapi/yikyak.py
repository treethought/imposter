import urllib.parse

from .web import WebObject
from .yak import Yak
from .yakker import Yakker


class YikYak(WebObject):
    def __init__(self):
        super().__init__()
        self._yakker = None

    @property
    def yakker(self):
        if not self._yakker:
            self._yakker = Yakker(self.auth_token, {})
            self._yakker.refresh()

        return self._yakker

    def login(self, country_code, phone_number, pin):
        """
        Login to YikYak and get our auth token

        See documentation for country codes

        Arguments:
            country_code (string): country code
            phone_number (string): phone number
            user_id (string): authentication PIN from app
        """
        self.auth_token = self.pair(country_code, phone_number, pin)

    def login_id(self, country_code, phone_number, user_id):
        """
        Alternate login with YikYak user ID instead of auth PIN

        Arguments:
            country_code (string): country code
            phone_number (string): phone number
            user_id (string): YikYak user ID
        """
        pin = self.init_pairing(user_id)
        self.auth_token = self.pair(country_code, phone_number, pin)

    def init_pairing(self, user_id):
        """
        Initialise web pairing and retrieve authentication PIN

        Arguments:
            user_id (string): YikYak user ID

        Returns:
            6 digit PIN code for use with pairing
        """
        url = "https://www.yikyak.com/api/auth/initPairing"
        data = {'userID': user_id}
        response = self._request('POST', url, data=data)
        return response['pin']

    def pair(self, country_code, phone_number, pin):
        """
        Login to YikYak to retrieve authentication token

        Arguments:
            country_code (string): 3-letter string representing country
            phone_number (string): phone number
            pin (string): authentication PIN generated by mobile app

        Returns:
            Authentication token required for further YikYak access
        """
        url = "https://www.yikyak.com/api/auth/pair"

        json = {
            'countryCode': country_code,
            'phoneNumber': phone_number,
            'pin': pin,
        }

        response = self._request('POST', url, json=json)
        return response

    def _get_yaks(self, url, latitude=0, longitude=0):
        """
        Retrieve Yaks from a URL

        Latitude and longitude will only affect Yak retrieval when searching
        based on location

        Arguments:
            url (string): Yak feed
            *latitude (number): latitude co-ordinate
            *longitude (number): longitude co-ordinate

        Returns:
            List of Yak objects from the feed
        """
        params = {
            'userLat': latitude,
            'userLong': longitude,
            'lat': latitude,
            'long': longitude,
            'myHerd': 0,
        }

        response = self._request('GET', url, params=params)

        # Generate new Yak objects from the JSON
        yaks = [Yak(self.auth_token, data) for data in response]
        return yaks

    def get_new_yaks(self, latitude, longitude):
        """
        Retrieve new Yaks from a location

        Arguments:
            latitude (float): location latitude
            longitude (float): location longitude

        Returns:
            List of Yak objects
        """

        url = 'https://www.yikyak.com/api/proxy/v1/messages/all/new'
        return self._get_yaks(url, latitude, longitude)

    def get_hot_yaks(self, latitude, longitude):
        """
        Retrieve hot Yaks from a location

        Arguments:
            latitude (float): location latitude
            longitude (float): location longitude

        Returns:
            List of Yak objects
        """
        url = 'https://www.yikyak.com/api/proxy/v1/messages/all/hot'
        return self._get_yaks(url, latitude, longitude)

    def get_my_hot_yaks(self):
        """
        Retrieve hot Yaks from user's post history

        Returns:
            List of Yak objects
        """
        url = 'https://www.yikyak.com/api/proxy/v1/yakker/history/yaks/hot'
        return self._get_yaks(url)

    def get_my_new_yaks(self):
        """
        Retrieve new Yaks from user's post history

        Returns:
            List of Yak objects
        """
        url = 'https://www.yikyak.com/api/proxy/v1/yakker/history/yaks/new'
        return self._get_yaks(url)

    def get_my_hot_replies(self):
        """
        Retrieve hot Yaks from user's comment history

        Returns:
            List of Yak objects
        """
        url = 'https://www.yikyak.com/api/proxy/v1/yakker/history/replies/hot'
        return self._get_yaks(url)

    def get_my_new_replies(self):
        """
        Retrieve new Yaks from user's comment history

        Returns:
            List of Yak objects
        """
        url = 'https://www.yikyak.com/api/proxy/v1/yakker/history/replies/new'
        return self._get_yaks(url)

    def get_yak(self, yak_id):
        """
        Retrieve a Yak by ID

        Arguments:
            yak_id (string): ID of Yak to retrieve

        Returns:
            Yak object
        """
        urlsafe_id = urllib.parse.quote_plus(yak_id)
        url = "https://www.yikyak.com/api/proxy/v1/messages/{}"
        url = url.format(urlsafe_id)
        params = {
            'userLat': 0,
            'userLong': 0,
        }

        data = self._request('GET', url, params=params)
        return Yak(self.auth_token, data)

    def compose_yak(self, message, latitude, longitude):
        """
        Compose a new Yak at a co-ordinate

        Arguments:
            message (string): contents of Yak
            latitude (float): location latitude
            longitude (float): location longitude
        """
        url = "https://www.yikyak.com/api/proxy/v1/messages"
        params = {
            'lat': latitude,
            'long': longitude,
            'myHerd': 0,
            'userLat': 0,
            'userLong': 0,
        }
        json = {
            'handle': True,
            'message': message,
        }

        data = self._request('POST', url, params=params, json=json)
        return Yak(self.auth_token, data)

    def check_handle_availability(self, handle):
        """
        Check availability of a handle

        Arguments:
            handle (string): handle to check

        Returns:
            Boolean representing availability
        """
        url = 'https://www.yikyak.com/api/proxy/v1/yakker/handles'
        params = {
            'handle': handle,
        }
        data = self._request('GET', url, params=params)
        return data['code'] == 0

    def claim_handle(self, handle):
        """
        Claim a handle

        Arguments:
            handle (string): handle to claim
        """
        url = 'https://www.yikyak.com/api/proxy/v1/yakker/handles'
        json = {
            'handle': handle,
        }
        data = self._request('POST', url, json=json)