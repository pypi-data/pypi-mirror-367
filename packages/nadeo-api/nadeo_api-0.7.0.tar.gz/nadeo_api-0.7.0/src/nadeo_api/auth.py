'''
| Author:   Ezio416
| Created:  2024-05-07
| Modified: 2025-08-05

- Functions for interacting with authentication tokens to use with the API
- Also contains variables and functions intended for internal use
'''

from base64 import b64encode, urlsafe_b64decode
from dataclasses import dataclass
from datetime import datetime as dt
import json
import time

import requests

from . import config
from . import util


audience_core:  str = 'NadeoServices'
audience_live:  str = 'NadeoLiveServices'  # also used for Meet endpoints (formerly known as Club)
audience_oauth: str = 'OAuth2'
tmnext_app_id:  str = '86263886-327a-4328-ac69-527f0d20a237'
url_core:       str = 'https://prod.trackmania.core.nadeo.online'
url_live:       str = 'https://live-services.trackmania.nadeo.live'
url_meet:       str = 'https://meet.trackmania.nadeo.club'
url_oauth:      str = 'https://api.trackmania.com'


@dataclass
class Token():
    '''
    - holds data on an authentication token
    - does not contain a base URL as a token could be used for multiple
    - if you wish to use this with other request libraries (such as `requests`), add to the request header: `{'Authorization': token.access_token}`

    Parameters
    ----------
    access_token: str
        - access token/ticket

    audience: str
        - audience for which token is valid

    refresh_token: str
        - token used to refresh access token if applicable
        - default: `''` (empty)

    server_account: bool
        - whether the token is for a dedicated server account instead of a Ubisoft account
        - default: `False`

    expiration: int
        - time at which access token/ticket will expire
        - if not given, will be decoded from the token's payload
        - default: `0`
    '''

    access_token:   str
    audience:       str
    expiration:     int
    refresh_token:  str
    server_account: bool
    token_decoded:  dict

    def __init__(self, access_token: str, audience: str, refresh_token: str = '', server_account: bool = False, expiration: int = 0):
        self.access_token = access_token
        self.audience = audience
        self.refresh_token = refresh_token
        self.server_account = server_account

        try:
            self.token_decoded = decode_jwt_from_token(self.access_token)
        except UnicodeDecodeError:
            pass

        if expiration != 0:
            self.expiration = expiration
        else:
            try:
                self.expiration = self.token_decoded['exp']
            except KeyError:
                self.expiration = int(time.time()) + 3600

    def __repr__(self) -> str:
        return f"nadeo_api.auth.Token('{self.audience}')"

    def __str__(self) -> str:
        return self.access_token

    @property
    def expired(self) -> bool:
        return int(time.time()) >= self.expiration

    def refresh(self) -> None:
        '''
        - refreshes a set of tokens if applicable
        - raises a `ValueError` if called on an OAuth2 token
        '''

        if self.audience == audience_oauth:
            raise ValueError('You may not refresh an OAuth2 token - request a new one instead.')

        req: requests.Response = requests.post(
            f'{url_core}/v2/authentication/token/refresh',
            headers={'Authorization': self.refresh_token},
            # json={'audience': self.audience}  # seems to not actually be required
        )

        if req.status_code >= 400:
            raise ConnectionError(f'Bad response refreshing token for {self.audience}: code {req.status_code}, response {req.text}')

        json: dict = req.json()
        self.access_token = f'nadeo_v1 t={json['accessToken']}'
        self.refresh_token = f'nadeo_v1 t={json['refreshToken']}'

        try:
            self.token_decoded = decode_jwt_from_token(self.access_token)
            self.expiration = self.token_decoded['exp']
        except KeyError:
            self.expiration = 0
        except UnicodeDecodeError:
            self.expiration = 0
            self.token_decoded = {}


def decode_jwt_from_token(token: str) -> dict:
    '''
    - decodes a JSON web token into a dictionary using its payload section
    - will fail if passed an invalid token such as an Ubisoft ticket
    '''

    payload:       str = token.split('.')[1]
    decoded_bytes: bytes = urlsafe_b64decode(f'{payload}==')
    decoded_str:   str = decoded_bytes.decode('utf-8')
    result:        dict = json.loads(decoded_str)

    return result


def _delete(token: Token, base_url: str, endpoint: str, params: dict = {}, body: dict = {}) -> dict | list:
    '''
    - sends a DELETE request to a specified API
    - this is for internal use - you should use an API-specific `delete` function instead

    Parameters
    ----------
    token: Token
        - authentication token from `auth.get_token()`

    base_url: str
        - base URL of desired API
        - must match your token's audience
        - valid: `url_core`, `url_live`, `url_meet`, `url_oauth`

    endpoint: str
        - desired endpoint or full URL
        - base URL and leading slash (`'https://.../'`) optional

    params: dict
        - request parameters if applicable
        - if you put parameters at the end of the `endpoint`, do not put them here or they will be duplicated
        - default: `{}` (empty)

    body: dict
        - request body if applicable
        - default: `{}` (empty)

    Returns
    -------
    dict | list
        - response body
    '''

    return _request(token, base_url, endpoint, params, 'delete', body)


def _get(token: Token, base_url: str, endpoint: str, params: dict = {}) -> dict | list:
    '''
    - sends a GET request to a specified API
    - this is for internal use - you should use an API-specific `get` function instead

    Parameters
    ----------
    token: Token
        - authentication token from `auth.get_token()`

    base_url: str
        - base URL of desired API
        - must match your token's audience
        - valid: `url_core`, `url_live`, `url_meet`, `url_oauth`

    endpoint: str
        - desired endpoint or full URL
        - base URL and leading slash (`'https://.../'`) optional

    params: dict
        - request parameters if applicable
        - if you put parameters at the end of the `endpoint`, do not put them here or they will be duplicated
        - default: `{}` (empty)

    Returns
    -------
    dict | list
        - response body
    '''

    return _request(token, base_url, endpoint, params)


def get_token(audience: str, username: str, password: str, agent: str = '', server_account: bool = False) -> Token:
    '''
    - requests an authentication token for a given audience

    Parameters
    ----------
    audience: str
        - desired audience for token use
        - capitalization is ignored
        - valid: `'NadeoServices'`/`'core'`/`'prod'`, `'NadeoLiveServices'`/`'live'`/`'meet'`/`'club'`, `'OAuth'`/`'OAuth2'`

    username: str
        - Ubisoft/dedicated server account username
        - for OAuth2, this is the identifier

    password: str
        - Ubisoft/dedicated server account password
        - for OAuth2, this is the secret

    agent: str
        - user agent with your program's name and a way to contact you
        - Ubisoft can block your request without this being properly set
        - not required for OAuth2
        - default: `''` (empty)

    server_account: bool
        - whether you're using a dedicated server account (Server usage) instead of a Ubisoft account (Client usage)
        - ignored when using OAuth2
        - default: `False`
    '''

    aud_lower: str = audience.lower()

    if aud_lower in ('nadeoservices', 'core', 'prod'):
        audience = audience_core
    elif aud_lower in ('nadeoliveservices', 'live', 'meet', 'club'):
        audience = audience_live
    elif aud_lower in ('oauth', 'oauth2'):
        audience = audience_oauth
    else:
        raise ValueError(f'Given audience is not valid: {audience}')

    util._log(audience)

    if audience == audience_oauth:
        req: requests.Response = requests.post(
            'https://api.trackmania.com/api/access_token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type':    'client_credentials',
                'client_id':     username,
                'client_secret': password
            }
        )

        if req.status_code >= 400:
            raise ConnectionError(f'Bad response getting token for {audience}: code {req.status_code}, response {req.text}')

        json: dict = req.json()
        return Token(json['access_token'], audience, expiration=int(time.time()) + json['expires_in'])

    if agent == '':
        raise ValueError('For web services endpoints, you must specify a user agent')

    req: requests.Response = requests.post(
        f'{url_core}/v2/authentication/token/basic' if server_account else 'https://public-ubiservices.ubi.com/v3/profiles/sessions',
        headers={
            'Authorization': f'Basic {b64encode(f'{username}:{password}'.encode('utf-8')).decode('ascii')}',
            'Content-Type':  'application/json',
            'Ubi-AppId':     tmnext_app_id,
            'User-Agent':    agent,
        },
        json={'audience': audience}
    )

    if req.status_code >= 400:
        raise ConnectionError(f'Bad response getting ticket for {audience}: code {req.status_code}, response {req.text}')

    json: dict = req.json()

    if server_account:
        return Token(f'nadeo_v1 t={json['accessToken']}', audience, f'nadeo_v1 t={json['refreshToken']}', True)

    ticket: Token = Token(f'ubi_v1 t={json['ticket']}', json['platformType'], expiration=int(dt.fromisoformat(json['expiration']).timestamp()))

    req2: requests.Response = requests.post(
        f'{url_core}/v2/authentication/token/ubiservices',
        headers={'Authorization': ticket.access_token},
        json={'audience': audience}
    )

    if req2.status_code >= 400:
        raise ConnectionError(f'Bad response getting token for {audience}: code {req.status_code}, response {req.text}')

    json2: dict = req2.json()
    return Token(f'nadeo_v1 t={json2['accessToken']}', audience, f'nadeo_v1 t={json2['refreshToken']}')


def _head(token: Token, base_url: str, endpoint: str, params: dict = {}) -> dict | list:
    '''
    - sends a HEAD request to a specified API
    - this is for internal use - you should use an API-specific `head` function instead

    Parameters
    ----------
    token: Token
        - authentication token from `auth.get_token()`

    base_url: str
        - base URL of desired API
        - must match your token's audience
        - valid: `url_core`, `url_live`, `url_meet`, `url_oauth`

    endpoint: str
        - desired endpoint or full URL
        - base URL and leading slash (`'https://.../'`) optional

    params: dict
        - request parameters if applicable
        - if you put parameters at the end of the `endpoint`, do not put them here or they will be duplicated
        - default: `{}` (empty)

    Returns
    -------
    dict | list
        - response body
    '''

    return _request(token, base_url, endpoint, params, 'head')


def _options(token: Token, base_url: str, endpoint: str, params: dict = {}, body: dict = {}) -> dict | list:
    '''
    - sends an OPTIONS request to a specified API
    - this is for internal use - you should use an API-specific `options` function instead

    Parameters
    ----------
    token: Token
        - authentication token from `auth.get_token()`

    base_url: str
        - base URL of desired API
        - must match your token's audience
        - valid: `url_core`, `url_live`, `url_meet`, `url_oauth`

    endpoint: str
        - desired endpoint or full URL
        - base URL and leading slash (`'https://.../'`) optional

    params: dict
        - request parameters if applicable
        - if you put parameters at the end of the `endpoint`, do not put them here or they will be duplicated
        - default: `{}` (empty)

    body: dict
        - request body if applicable
        - default: `{}` (empty)

    Returns
    -------
    dict | list
        - response body
    '''

    return _request(token, base_url, endpoint, params, 'options', body)


def _patch(token: Token, base_url: str, endpoint: str, params: dict = {}, body: dict = {}) -> dict | list:
    '''
    - sends a PATCH request to a specified API
    - this is for internal use - you should use an API-specific `patch` function instead

    Parameters
    ----------
    token: Token
        - authentication token from `auth.get_token()`

    base_url: str
        - base URL of desired API
        - must match your token's audience
        - valid: `url_core`, `url_live`, `url_meet`, `url_oauth`

    endpoint: str
        - desired endpoint or full URL
        - base URL and leading slash (`'https://.../'`) optional

    params: dict
        - request parameters if applicable
        - if you put parameters at the end of the `endpoint`, do not put them here or they will be duplicated
        - default: `{}` (empty)

    body: dict
        - request body if applicable
        - default: `{}` (empty)

    Returns
    -------
    dict | list
        - response body
    '''

    return _request(token, base_url, endpoint, params, 'patch', body)


def _post(token: Token, base_url: str, endpoint: str, params: dict = {}, body: dict = {}) -> dict | list:
    '''
    - sends a POST request to a specified API
    - this is for internal use - you should use an API-specific `post` function instead

    Parameters
    ----------
    token: Token
        - authentication token from `auth.get_token()`

    base_url: str
        - base URL of desired API
        - must match your token's audience
        - valid: `url_core`, `url_live`, `url_meet`, `url_oauth`

    endpoint: str
        - desired endpoint or full URL
        - base URL and leading slash (`'https://.../'`) optional

    params: dict
        - request parameters if applicable
        - if you put parameters at the end of the `endpoint`, do not put them here or they will be duplicated
        - default: `{}` (empty)

    body: dict
        - request body if applicable
        - default: `{}` (empty)

    Returns
    -------
    dict | list
        - response body
    '''

    return _request(token, base_url, endpoint, params, 'post', body)


def _put(token: Token, base_url: str, endpoint: str, params: dict = {}, body: dict = {}) -> dict | list:
    '''
    - sends a PUT request to a specified API
    - this is for internal use - you should use an API-specific `put` function instead

    Parameters
    ----------
    token: Token
        - authentication token from `auth.get_token()`

    base_url: str
        - base URL of desired API
        - must match your token's audience
        - valid: `url_core`, `url_live`, `url_meet`, `url_oauth`

    endpoint: str
        - desired endpoint or full URL
        - base URL and leading slash (`'https://.../'`) optional

    params: dict
        - request parameters if applicable
        - if you put parameters at the end of the `endpoint`, do not put them here or they will be duplicated
        - default: `{}` (empty)

    body: dict
        - request body if applicable
        - default: `{}` (empty)

    Returns
    -------
    dict | list
        - response body
    '''

    return _request(token, base_url, endpoint, params, 'put', body)


def _request(token: Token, base_url: str, endpoint: str, params: dict = {}, method: str = 'get', body: dict = {}) -> dict | list:
    '''
    - sends a request to a specified API
    - this is for internal use - you should use an explicit function like `core.get()` instead

    Parameters
    ----------
    token: Token
        - authentication token from `auth.get_token()`

    base_url: str
        - base URL of desired API
        - must match your token's audience
        - valid: `url_core`, `url_live`, `url_meet`, `url_oauth`

    endpoint: str
        - desired endpoint or full URL
        - base URL and leading slash (`'https://.../'`) optional

    params: dict
        - parameters for request if applicable
        - if you put parameters at the end of the `endpoint`, do not put them here or they will be duplicated
        - default: `{}` (empty)

    method: str
        - type of request to send
        - valid: `'delete'`, `'get'`, `'head'`, `'options'`, `'patch'`, `'post'`, `'put'`
        - default: `'get'`

    body: dict
        - request body
        - default: `{}` (empty)

    Returns
    -------
    dict | list
        - response body
    '''

    util._log(f'{method.upper()} {base_url}/{endpoint} | params: {params} | body: {body}')

    if (base_url := base_url.lower()) not in (url_core, url_live, url_meet, url_oauth):
        raise ValueError(f'Given base URL is invalid: {base_url}')

    if (method := method.lower()) not in ('delete', 'get', 'head', 'options', 'patch', 'post', 'put'):
        raise ValueError(f'Given method is invalid: {method}')

    base_name: str = 'Core'

    if base_url == url_core:
        if token.audience != audience_core:
            raise ValueError(f'Mismatched audience and base URL: {token.audience} | {base_url}')

    elif base_url in (url_live, url_meet):
        if token.audience != audience_live:
            raise ValueError(f'Mismatched audience and base URL: {token.audience} | {base_url}')

        base_name = 'Live' if base_url == url_live else 'Meet'

    else:
        if token.audience != audience_oauth:
            raise ValueError(f'Mismatched audience and base URL: {token.audience} | {base_url}')

        base_name = audience_oauth

    if token.expired:
        token.refresh()

    if endpoint.startswith(base_url):
        endpoint = endpoint.split(base_url)[1]

    if endpoint.startswith('/'):
        endpoint = endpoint[1:]

    def __request() -> requests.Response:
        _wait()
        return getattr(requests, method)(  # trust that requests never breaks this
            url=f'{base_url}/{endpoint}',
            params=params,
            headers={'Authorization': token.access_token},
            json=body
        )

    req: requests.Response = __request()

    if req.status_code == 401:  # token may have expired prematurely
        token.refresh()
        req = __request()

    if req.status_code >= 400:
        raise ConnectionError(f'Bad response from {base_name} API: code {req.status_code}, response {req.text}')

    return req.json()


def _wait() -> None:
    now: int = util.stamp(True)
    if now - config._last_request_timestamp < config.wait_between_requests_ms:
        util._log('')
        time.sleep(float(config._last_request_timestamp + config.wait_between_requests_ms - now) / 1000.0)
        config._last_request_timestamp = util.stamp(True)
    else:
        config._last_request_timestamp = now
