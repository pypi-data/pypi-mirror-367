class SDKConfig:
    def __init__(self, builder):
        self._base_url = builder._base_url
        self._timeout = builder._timeout
        self._max_retries = builder._max_retries
        self._max_connections = builder._max_connections
        self._enable_logging = builder._enable_logging
        self._app_key = builder._app_key
        self._app_secret = builder._app_secret
        self._token_cache_time = builder._token_cache_time
        self._login_type = builder._login_type
        self._upload_path = builder._upload_path

    @property
    def base_url(self):
        return self._base_url

    @property
    def timeout(self):
        return self._timeout

    @property
    def max_retries(self):
        return self._max_retries

    @property
    def max_connections(self):
        return self._max_connections

    @property
    def enable_logging(self):
        return self._enable_logging

    @property
    def app_key(self):
        return self._app_key

    @property
    def app_secret(self):
        return self._app_secret

    @property
    def token_cache_time(self):
        return self._token_cache_time

    @property
    def login_type(self):
        return self._login_type

    @property
    def upload_path(self):
        return self._upload_path

    class Builder:
        def __init__(self):
            self._base_url = "https://api.example.com"
            self._timeout = 5000
            self._max_retries = 3
            self._max_connections = 10
            self._enable_logging = False
            self._app_key = ""
            self._app_secret = ""
            self._token_cache_time = 55
            self._login_type = "3"

        def base_url(self, base_url):
            self._base_url = base_url
            return self

        def timeout(self, timeout):
            self._timeout = timeout
            return self

        def max_retries(self, max_retries):
            self._max_retries = max_retries
            return self

        def max_connections(self, max_connections):
            self._max_connections = max_connections
            return self

        def enable_logging(self, enable_logging):
            self._enable_logging = enable_logging
            return self

        def app_key(self, app_key):
            self._app_key = app_key
            return self

        def app_secret(self, app_secret):
            self._app_secret = app_secret
            return self

        def token_cache_time(self, token_cache_time):
            self._token_cache_time = token_cache_time
            return self

        def login_type(self, login_type):
            self._login_type = login_type
            return self

        def upload_path(self, upload_path):
            self._upload_path = upload_path
            return self

        def build(self):
            return SDKConfig(self)
