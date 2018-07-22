import json

from requests_oauthlib import OAuth1Session

from py_trace.exceptions import ApiError

class Trace():
    """ """
    def __init__(self, client_key, client_secret, callback_uri=None, access_token=None,
                 sport='snow'):
        """

        :param str client_key: Client key obtained from Trace
        :param str client_secret: Client secret obtained from Trace
        :param str callback_uri: URL for auth callback, leave None if using command line
            (Default value = None)
        :param dict access_token: If already authenticated, reuse the given oauth_token
            and oauth_token_secret (Default value = None)
        :param str sport: Which sport API to use, 'snow' or 'surf'
            (Default value = 'snow')

        """
        self._client_key = client_key
        self._client_secret = client_secret
        self._callback_uri = callback_uri

        if sport == 'snow':
            subdomain = 'www'
        elif sport == 'surf':
            subdomain = 'surf'
        else:
            raise ValueError('Invalid value for "sport", should be "surf" or "snow"')

        self.API_BASE = 'https://{0}.alpinereplay.com/api/'.format(subdomain)
        self.AUTHORIZATION_URL = self.API_BASE + 'oauth_login'
        self.REQUEST_TOKEN_URL = self.API_BASE + 'oauth_init'
        self.ACCESS_TOKEN_URL = self.API_BASE + 'oauth_access_token'
        self.API_VERSION = '1'
        self.API_URL = self.API_BASE + 'v' + self.API_VERSION

        if access_token is not None:
            self.authenticate(access_token)

    def get_request_token(self):
        """
        Step 1 of auth, get the request token. This is optional as this is called
        by get_auth_url if needed.

        """
        self.session = OAuth1Session(
            client_key=self._client_key,
            client_secret=self._client_secret,
            callback_uri=self._callback_uri
        )
        self.request_token = self.session.fetch_request_token(self.REQUEST_TOKEN_URL)
        return self.request_token

    def get_authorization_url(self):
        """
        Step 2 of auth, get the authorization URL. It will first get the request
        token if it needs it.

        """
        if getattr(self, 'request_token', None) is None:
            self.get_request_token()
        return self.session.authorization_url(self.AUTHORIZATION_URL)

    def get_access_token(self, oauth_verifier):
        """
        Step 3 of auth, get the access token. After the user authorizes the app,
        we get the access token using the oauth_verifier and then authenticate the user.

        :param str oauth_verifier: A string containing the verifier

        """
        self.session = OAuth1Session(
            client_key=self._client_key,
            client_secret=self._client_secret,
            resource_owner_key=self.request_token.get('oauth_token'),
            resource_owner_secret=self.request_token.get('oauth_token_secret'),
            verifier=oauth_verifier
        )

        self.access_token = self.session.fetch_access_token(self.ACCESS_TOKEN_URL)

        self.authenticate(self.access_token)

        del self.request_token

        return self.access_token

    def authenticate(self, access_token):
        """
        Step 4 of auth, authenticate the user by creating a session with the
        access token. This is optional as it is called by get_access_token.
        If you already have the access_token, you can call this
        function directly or pass the access_token when instanciating
        the class in order to authenticate.

        :param dict access_token: A dict containing the oauth_token and
            oauth_token_secret.

        """
        self.session = OAuth1Session(
            client_key=self._client_key,
            client_secret=self._client_secret,
            resource_owner_key=access_token.get('oauth_token'),
            resource_owner_secret=access_token.get('oauth_token_secret')
        )

    def api_request(self, path, method='GET', **kwargs):
        """
        Make a request to the API and parse the results

        :param str path: API endpoint to hit, must start with /
        :param str method: HTTP method (Default value = 'GET')
        :param **kwargs: Arguments to pass to the request, see
            :any:`requests.request`

        """
        res = self.session.request(method, self.API_URL + path, **kwargs).json()
        if res['success']:
            return res['data']
        else:
            raise ApiError(res['error'])

    def get_user(self, user_id='self'):
        """
        Get user info

        :param int,str user_id: User ID (Default value = 'self')
        """
        return self.api_request('/users/{0}'.format(user_id))

    def get_visits(self, user_id='self', limit=None, min_timestamp=None,
                   max_timestamp=None, visit_ids=None, ffilter=None):
        """
        Get all user visits

        :param int,str user_id: User ID (Default value = 'self')
        :param str,int limit: Limit the number of entries in responses, if None is given
            the API defaults to 50 (Default value = None)
        :param int min_timestamp: Minimum timestamp to filter results (Default value = None)
        :param int max_timestamp: Maximum timestamp to filter results (Default value = None)
        :param list visit_ids: List of visit IDs to include (Default value = None)
        :param dict ffilter: A filter for fields to be returned, see
            `documentation <http://developers.traceup.com/Requests_and_Responses.html>`_
            for more (Default value = None)

        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        if min_timestamp is not None:
            params['min_timestamp'] = min_timestamp
        if max_timestamp is not None:
            params['max_timestamp'] = max_timestamp
        if visit_ids is not None:
            params['visit_ids'] = visit_ids
        if ffilter is not None:
            params['filter'] = json.dumps(ffilter)

        res = self.api_request('/users/{0}/visits'.format(user_id),
                               params=params)

        for visit in res:
            visit['total_time'] = visit['lift_time'] + \
                visit['slope_time'] + \
                visit['rest_time']

        return res

    def get_visit_list(self, user_id='self', ffilter=None):
        """
        Get list of user visits

        :param int,str user_id: User ID (Default value = 'self')
        :param dict ffilter: A filter for fields to be returned, see
            `documentation <http://developers.traceup.com/Requests_and_Responses.html>`_
            for more (Default value = None)

        """
        params = {}
        if ffilter is not None:
            params['filter'] = json.dumps(ffilter)

        return self.api_request('/users/{0}/visits/list'.format(user_id),
                                params=params)

    def create_visit_overlay(self, data):
        """
        Upload track file to create video overlay

        :param data:

        """
        return self.api_request('/users/self/visit-overlay', 'POST',
                                data=data)

    def create_visit_comment(self, visit_id, facebook=False, twitter=False, photo=None,
                             hide_resort_name=0, comment=None, equipment=None):
        """
        Add comment to a visit

        :param int,str visit_id: Visit ID
        :param bool facebook: Whether to post to facebook or not (Default value = False)
        :param bool twitter: Whether to post to twitter or not (Default value = False)
        :param photo: (Default value = None)
        :param hide_resort_name: (Default value = 0)
        :param str comment: Comment text (Default value = None)
        :param list equipment: List of strings for each equipment item (Default value = None)

        """
        data = {
            'facebook': facebook,
            'twitter': twitter,
            'hide_resort_name': hide_resort_name,
        }

        if photo is not None:
            data['photo'] = photo
        if comment is not None:
            data['comment'] = comment
        if equipment is not None:
            data['equipment'] = equipment

        return self.api_request('/visits/{0}/comment'.format(visit_id), 'POST',
                                data=data)

    def create_visit_photo(self, visit_id, photo):
        """
        Add a photo to a visit

        :param int,str visit_id: Visit ID
        :param photo:

        """
        data = {'photo': photo}
        return self.api_request('/visits/{0}/photo'.format(visit_id), 'POST',
                                data=data)

    def share_visit(self, visit_id, stats, comment=None, photo=None, facebook=True,
                    twitter=True):
        """
        Share a visit

        :param int,str visit_id: Visit ID
        :param list stats: List of stats to include, one of [total_distance, jumps,
            air_time, avg_speed, calories, vertical_drop, sustained_speed, slope_time,
            max_slope, turns_num, longest_ride]
        :param str comment: Comment text (Default value = None)
        :param photo: (Default value = None)
        :param bool facebook: Whether to post to facebook or not (Default value = True)
        :param bool twitter: Whether to post to twitter or not (Default value = True)

        """

        data = {
            'stats': stats,
            'facebook': facebook,
            'twitter': twitter,
        }

        if photo is not None:
            data['photo'] = photo
        if comment is not None:
            data['comment'] = comment

        return self.api_request('/visits/{0}/share'.format(visit_id), 'POST',
                                data=data)

    def create_visit_export(self, visit_id):
        """
        Create an export of the visit gpx file

        :param int,str visit_id: Visit ID

        """
        return self.api_request('/visits/{0}/export'.format(visit_id), 'POST')

    def get_visit_weather(self, visit_id):
        """
        Get weather report for visit if available

        :param int,str visit_id: Visit ID

        """
        return self.api_request('/visits/{0}/weather'.format(visit_id))

    def get_visit_equipment(self, visit_id):
        """
        Get equipment info for a visit

        :param int,str visit_id: Visit ID

        """
        return self.api_request('/visits/{0}/equipment'.format(visit_id))

    def create_visit_equipment(self, visit_id, equipment):
        """
        Add equipment info for a visit

        :param int,str visit_id: Visit ID
        :param list equipment: List of strings for each equipment item

        """
        data = {'equipment': equipment}
        return self.api_request('/visits/{0}/equipment'.format(visit_id), 'POST',
                                data=data)

    def hide_run(self, run_id):
        """
        Hide a run

        :param int,str run_id: Run ID

        """
        return self.api_request('/runs/{0}/hide'.format(run_id), 'POST')

    def delete_run(self, run_id):
        """
        Delete a run

        :param int,str run_id: Run ID

        """
        return self.api_request('/runs/{0}/delete'.format(run_id), 'POST')

    def get_events(self, min_timestamp=None, max_timestamp=None, limit=None,
                   ffilter=None):
        """
        Get all events for yourself

        :param int min_timestamp: Minimum timestamp to filter results (Default value = None)
        :param int max_timestamp: Maximum timestamp to filter results (Default value = None)
        :param str,int limit: Limit the number of entries in responses, if None is given
            the API defaults to 50 (Default value = None)
        :param dict ffilter: A filter for fields to be returned, see
            `documentation <http://developers.traceup.com/Requests_and_Responses.html>`_
            for more (Default value = None)

        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        if min_timestamp is not None:
            params['min_timestamp'] = min_timestamp
        if max_timestamp is not None:
            params['max_timestamp'] = max_timestamp
        if ffilter is not None:
            params['filter'] = json.dumps(ffilter)

        return self.api_request('/users/self/events', params=params)

    def like_event(self, event_id):
        """
        Like an event

        :param int,str event_id: Event ID

        """
        return self.api_request('/events/{0}/like', 'POST')

    def unlike_event(self, event_id):
        """
        Unlike an event

        :param int,str event_id: Event ID

        """
        return self.api_request('/events/{0}/unlike', 'POST')

    def create_event_comment(self, event_id, message):
        """
        Add a comment to an event

        :param int,str event_id: Event ID
        :param str message: Comment text

        """
        data = {'message': message}
        return self.api_request('/events/{0}/comment', 'POST',
                                data=data)

    def get_event(self, event_id):
        """
        Get event info

        :param int,str event_id: Event ID

        """
        return self.api_request('/events/{0}'.format(event_id))

    def get_visit_events(self, visit_id, ffilter=None):
        """
        Get all events for a visit

        :param int,str visit_id: Visit ID
        :param dict ffilter: A filter for fields to be returned, see
            `documentation <http://developers.traceup.com/Requests_and_Responses.html>`_
            for more (Default value = None)

        """
        params = {}
        if ffilter is not None:
            params['filter'] = json.dumps(ffilter)

        return self.api_request('/visits/{0}/events'.format(visit_id),
                                params=ffilter)
