import datetime
from .._abstract import abstract
########################################################################
class OAuthSecurityHandler(abstract.BaseSecurityHandler):
    """Handles AGOL OAuth Security
       Inputs:
          client_id - OAuth client key
          secret_id - OAuth secret key
          token_url - optional - url to where the token is obtained
          proxy_url - optional - proxy url as a string
          proxy_port - optional - proxy port as integer
       Output:
          OAuthSecurityHandler Class Object
    """
    _token = None
    _default_token_url = "https://www.arcgis.com/sharing/oauth2/token"
    _token_url = "https://www.arcgis.com/sharing/oauth2/token"
    _client_id = None
    _secret_id = None
    _token_created_on = None
    _token_expires_on = None
    _expires_in = None
    _proxy_url = None
    _proxy_port = None
    #----------------------------------------------------------------------
    def __init__(self, client_id, secret_id, token_url=None,
                 proxy_url=None, proxy_port=None):
        """Constructor"""
        self._client_id = client_id
        self._secret_id = secret_id
        self._token_url = token_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
        self._token_expires_on = datetime.datetime.now() + datetime.timedelta(seconds=600)
    #----------------------------------------------------------------------
    @property
    def proxy_url(self):
        """gets the proxy url"""
        return self._proxy_url
    #----------------------------------------------------------------------
    @proxy_url.setter
    def proxy_url(self, value):
        """ sets the proxy_url """
        self._proxy_url = value
    #----------------------------------------------------------------------
    @property
    def proxy_port(self):
        """ gets the proxy port """
        return self._proxy_port
    #----------------------------------------------------------------------
    @proxy_port.setter
    def proxy_port(self, value):
        """ sets the proxy port """
        if isinstance(value, int):
            self._proxy_port = value
    #----------------------------------------------------------------------
    @property
    def token(self):
        """ obtains a token from the site """
        if self._token is None or \
           datetime.datetime.now() >= self._token_expires_on:
            self._generateForOAuthSecurity(self._client_id,
                                      self._secret_id,
                                      self._token_url)
        return self._token
    #----------------------------------------------------------------------
    @property
    def client_id(self):
        """ returns the client id """
        return self._client_id
    #----------------------------------------------------------------------
    @client_id.setter
    def client_id(self, value):
        """ sets the client id for oauth """
        self._token = None
        self._client_id = value
    #----------------------------------------------------------------------
    @property
    def secret_id(self):
        """ returns ***** for secret id """
        return "*****"
    #----------------------------------------------------------------------
    @secret_id.setter
    def secret_id(self, value):
        """ sets the secret id """
        self._token = None
        self._secret_id = value
    #----------------------------------------------------------------------
    @property
    def token_url(self):
        """ returns the token url """
        return self._token_url
    #----------------------------------------------------------------------
    @token_url.setter
    def token_url(self, value):
        """ sets the token url """
        self._token = None
        self._token_url = value
    #----------------------------------------------------------------------
    def resetTokenURLToDefault(self):
        """ resets the token url to the default url """
        self._token = None
        self._token_url = self._default_token_url
    #----------------------------------------------------------------------
    @property
    def tokenExperationDate(self):
        """ returns when the token is not valid """
        return self._token_expires_on
    #----------------------------------------------------------------------
    @property
    def tokenObtainedDate(self):
        """ returns when the token was generated """
        return self._token_created_on
    #----------------------------------------------------------------------
    def _generateForOAuthSecurity(self, client_id,
                                 secret_id, token_url=None):
        """ generates a token based on the OAuth security model """
        grant_type="client_credentials"
        if token_url is None:
            token_url = "https://www.arcgis.com/sharing/oauth2/token"
        params = {
            "client_id" : client_id,
            "client_secret" : secret_id,
            "grant_type":grant_type,
            "f" : "json"
        }
        token = self._do_get(url=token_url, param_dict=params,
                             proxy_port=self._proxy_port, proxy_url=self._proxy_url)

        if 'access_token' in token:
            self._token = token['access_token']
            self._expires_in = token['expires_in']
            self._token_created_on = datetime.datetime.now()
            self._token_expires_on = self._token_created_on + datetime.timedelta(seconds=int(token['expires_in']))
        else:
            self._token = None
            self._expires_in = None
            self._token_created_on = None
            self._token_expires_on = None
            #self._token_expires_on = None
########################################################################
class AGOLTokenSecurityHandler(abstract.BaseSecurityHandler):
    """ handles ArcGIS Online Token Base Security
        username - required - username to access AGOL services
        password - required - password for username above
        token_url - optional - if URL is different than default AGOL token
                    url, then enter it here for AGOL token service.
        proxy_url - optional - if proxy is required to access internet, the
                    IP goes here.
        proxy_post - optional - if proxy is used and it's not port 90 enter
                     it here.
    """
    _token = None

    _surl = None
    _org_url ="http://www.arcgis.com"
    _url = "https://www.arcgis.com/sharing/rest"
    _referer_url = None

    _username = None
    _password = None
    _token_url = None
    _default_token_url = 'https://arcgis.com/sharing/rest/generateToken'
    _token_created_on = None
    _token_expires_on = None
    _expires_in = None
    _proxy_url = None
    _proxy_port = None
    _valid = True
    _message = ""
    #----------------------------------------------------------------------
    def __init__(self, username, password,org_url ="https://www.arcgis.com", token_url=None,
                 proxy_url=None, proxy_port=None):
        """Constructor"""
        self._username = username
        self._password = password
        self._token_url = token_url
        self._org_url = org_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
        self._token_expires_on = datetime.datetime.now() + datetime.timedelta(seconds=600)
        self._initURL(token_url=token_url)
    #----------------------------------------------------------------------
    def _initURL(self, org_url=None,
                rest_url=None, token_url=None,
                referer_url=None):
        """ sets proper URLs for AGOL """
        if org_url is not None and org_url != '':
            if not org_url.startswith('http://') and not org_url.startswith('https://'):
                org_url = 'http://' + org_url
            self._org_url = org_url
        if not self._org_url.startswith('http://') and not self._org_url.startswith('https://'):
            self._org_url = 'http://' + self._org_url
        if rest_url is not None:
            self._url = rest_url
        else:
            self._url = self._org_url + "/sharing/rest"

        if self._url.startswith('http://'):
            self._surl = self._url.replace('http://', 'https://')
        else:
            self._surl  =  self._url

        if token_url is None:
            self._token_url = self._surl  + '/generateToken'
        else:
            self._token_url = token_url

        if referer_url is None:
            if not self._org_url.startswith('http://'):
                self._referer_url = self._org_url.replace('http://', 'https://')
            else:
                self._referer_url = self._org_url
        else:
            self._referer_url = referer_url
    #---------------------------------------------------------------------- 
    @property
    def message(self):
        """ returns any messages """
        return self._message   
    #----------------------------------------------------------------------
    @property
    def valid(self):
        """ returns boolean wether handler is valid """
        return self._valid
    #----------------------------------------------------------------------
    @property
    def org_url(self):
        """ gets/sets the organization URL """
        return self._org_url
    #----------------------------------------------------------------------
    @org_url.setter
    def org_url(self, value):
        """ gets/sets the organization URL """
        if value is not None:
            self._org_url = value
    #----------------------------------------------------------------------
    @property
    def proxy_url(self):
        """gets the proxy url"""
        return self._proxy_url
    #----------------------------------------------------------------------
    @proxy_url.setter
    def proxy_url(self, value):
        """ sets the proxy_url """
        self._proxy_url = value
    #----------------------------------------------------------------------
    @property
    def proxy_port(self):
        """ gets the proxy port """
        return self._proxy_port
    #----------------------------------------------------------------------
    @proxy_port.setter
    def proxy_port(self, value):
        """ sets the proxy port """
        if isinstance(value, int):
            self._proxy_port = value
    #----------------------------------------------------------------------
    @property
    def username(self):
        """ returns the username """
        return self._username
    #----------------------------------------------------------------------
    @username.setter
    def username(self, username):
        """ sets the username """
        self._token = None
        self._username = username
    #----------------------------------------------------------------------
    @property
    def password(self):
        """ returns **** for the password """
        return "****"
    #----------------------------------------------------------------------
    @password.setter
    def password(self, value):
        """ sets the password """
        self._token = None
        self._password = value
    #----------------------------------------------------------------------
    @property
    def token_url(self):
        """ returns the token url """
        if self._token_url is None:
            return self._default_token_url
        return self._token_url
    #----------------------------------------------------------------------
    @token_url.setter
    def token_url(self, value):
        """ sets the token url """
        self._token = None
        self._token_url = value
    #----------------------------------------------------------------------
    def resetTokenURLToDefault(self):
        """ resets the token url to the default url """
        self._token = None
        self._token_url = self._default_token_url
    #----------------------------------------------------------------------
    @property
    def tokenExperationDate(self):
        """ returns when the token is not valid """
        return self._token_expires_on
    #----------------------------------------------------------------------
    @property
    def tokenObtainedDate(self):
        """ returns when the token was generated """
        return self._token_created_on
    #----------------------------------------------------------------------
    @property
    def referer_url(self):
        """ returns when the token was generated """
        return self._referer_url    
    #----------------------------------------------------------------------
    @property
    def token(self):
        """ returns the token for the site """
        if self._token is None or \
           datetime.datetime.now() >= self._token_expires_on:
            result = self._generateForTokenSecurity(username=self._username,
                                           password=self._password,
                                           referer=self._referer_url,
                                           tokenUrl=self._token_url)
            if 'error' in result:
                self._valid = False
                self._message = result
            else:
                self._valid = True
                self._message = "Token Generated"
        return self._token
    #----------------------------------------------------------------------
    def _generateForTokenSecurity(self,
                                  username,
                                  password,
                                  referer=None,
                                  tokenUrl=None,
                                  expiration=None,
                                  proxy_url=None,
                                  proxy_port=None):
        """ generates a token for a feature service """
        if referer is None:
            referer = self._referer_url
        if tokenUrl is None:
            tokenUrl  = self._token_url

        query_dict = {'username': self._username,
                      'password': self._password,
                      'expiration': str(60),
                      'referer': referer,
                      'f': 'json'}
        if expiration is not None:
            query_dict['expiration'] = str(expiration)
        self._token_created_on = datetime.datetime.now()
        token = self._do_post(url=tokenUrl,
                              param_dict=query_dict,
                              proxy_url=self._proxy_url,
                              proxy_port=self._proxy_port)
        if 'error' in token:
            self._token = None
            return token
        if token['expires'] > 86400:
            seconds = 86400
        else:
            seconds = int(token['expires'])
        self._token_expires_on = self._token_created_on + \
            datetime.timedelta(seconds=seconds)
        if "token" not in token:
            self._token = None
            return None
        else:
            httpPrefix = self._url
            if token['ssl'] == True:
                httpPrefix = self._surl
            self._token = token['token']
            return token['token'], httpPrefix
#########################################################################
class AGSTokenSecurityHandler(abstract.BaseSecurityHandler):
    """ handles ArcGIS Server Security
        username - required - person accessing server
        password - required - login credential
        token_url - required - URL to generate a token on server
        proxy_url - optional - IP of proxy
        proxy_port - optional - port of the proxy server
    """
    _token = None
    _username = None
    _password = None
    _token_url = None
    _token_created_on = None
    _token_expires_on = None
    _expires_in = None
    _proxy_url = None
    _proxy_port = None
    _default_token_url = None
    #----------------------------------------------------------------------
    def __init__(self, username, password, token_url,
                 proxy_url=None, proxy_port=None):
        """Constructor"""
        self._username = username
        self._password = password
        self._token_url = token_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
        self._token_expires_on = datetime.datetime.now() + datetime.timedelta(seconds=600)
    #----------------------------------------------------------------------
    @property
    def proxy_url(self):
        """gets the proxy url"""
        return self._proxy_url
    #----------------------------------------------------------------------
    @proxy_url.setter
    def proxy_url(self, value):
        """ sets the proxy_url """
        self._proxy_url = value
    #----------------------------------------------------------------------
    @property
    def proxy_port(self):
        """ gets the proxy port """
        return self._proxy_port
    #----------------------------------------------------------------------
    @proxy_port.setter
    def proxy_port(self, value):
        """ sets the proxy port """
        if isinstance(value, int):
            self._proxy_port = value
    #----------------------------------------------------------------------
    @property
    def username(self):
        """ returns the username """
        return self._username
    #----------------------------------------------------------------------
    @username.setter
    def username(self, username):
        """ sets the username """
        self._token = None
        self._username = username
    #----------------------------------------------------------------------
    @property
    def password(self):
        """ returns **** for the password """
        return "****"
    #----------------------------------------------------------------------
    @password.setter
    def password(self, value):
        """ sets the password """
        self._token = None
        self._password = value
    #----------------------------------------------------------------------
    @property
    def token_url(self):
        """ returns the token url """
        return self._token_url
    #----------------------------------------------------------------------
    @token_url.setter
    def token_url(self, value):
        """ sets the token url """
        self._token = None
        self._token_url = value
    #----------------------------------------------------------------------
    @property
    def tokenExperationDate(self):
        """ returns when the token is not valid """
        return self._token_expires_on
    #----------------------------------------------------------------------
    @property
    def tokenObtainedDate(self):
        """ returns when the token was generated """
        return self._token_created_on
    #----------------------------------------------------------------------
    @property
    def token(self):
        """ returns the token for the site """
        if self._token is None or \
           datetime.datetime.now() >= self._token_expires_on:
            self._generateForTokenSecurity(username=self._username,
                                           password=self._password,
                                           tokenUrl=self._token_url)
        return self._token
    #----------------------------------------------------------------------
    def _generateForTokenSecurity(self,
                                  username, password,
                                  tokenUrl, expiration=None):
        """ generates a token for a feature service """
        query_dict = {'username': username,
                      'password': password,
                      'client': 'requestip',
                      'f': 'json'}
        if expiration is not None:
            query_dict['expiration'] = expiration
        token = self._do_post(url=tokenUrl, param_dict=query_dict,
                              proxy_port=self._proxy_port, proxy_url=self._proxy_url)
        if "token" not in token:
            self._token = None
            self._token_created_on = None
            self._token_expires_on = None
            self._expires_in = None
            return None
        else:
            self._token = token['token']
            self._token_created_on = datetime.datetime.now()
            if token['expires'] > 86400:
                seconds = 86400
            else:
                seconds = int(token['expires'])
            self._token_expires_on = self._token_created_on + datetime.timedelta(seconds=seconds)
            self._expires_in = token['expires']
            return token['token']
########################################################################
class PortalTokenSecurityHandler(abstract.BaseSecurityHandler):
    """
    Handles connection to a Portal Site

    Inputs:
       username - name of the user
       password - password for user
       org_Url - base organization URL
                    ex: https://chronus.com/arcgis/
       proxy_url - URL of the proxy
       proxy_port - proxy port
    """
    _token = None
    _server_token = None
    _server_token_expires_on = None
    _server_token_created_on = None
    _server_expires_in = None    
    _server_url = None
    _org_url = None
    _url = None
    _username = None
    _password = None
    _proxy_port = None
    _proxy_url = None
    _token_url = None
    _token_created_on = None
    _token_expires_on = None
    _expires_in = None
    _valid = True
    _message = ""    
    #----------------------------------------------------------------------
    def __init__(self,
                 username,
                 password,
                 org_url,
                 token_url=None,
                 proxy_url=None,
                 proxy_port=None):
        """Constructor"""
        self._org_url = org_url
        self._username = username
        self._password = password
        
        self._token_url = token_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url  
        self._token_expires_on = datetime.datetime.now() + datetime.timedelta(seconds=300)
       
        self._initURL()
    #----------------------------------------------------------------------         
            
    def _initURL(self, referer_url=None):
        """ sets proper URLs for Portal """
        if self._org_url is not None and self._org_url != '':
            if not self._org_url.startswith('http://') and not self._org_url.startswith('https://'):
                self._org_url = 'https://' + self._org_url
           
       
        self._url = self._org_url + "/sharing/rest"

     
        if self._token_url is None:
            self._token_url = self._url  + '/generateToken'

        if referer_url is None:
            
            self._referer_url = self._org_url
        else:
            self._referer_url = referer_url
    #---------------------------------------------------------------------- 
    @property
    def message(self):
        """ returns any messages """
        return self._message   
    #----------------------------------------------------------------------
    @property
    def valid(self):
        """ returns boolean wether handler is valid """
        return self._valid
    #----------------------------------------------------------------------
    @property
    def org_url(self):
        """ gets/sets the organization URL """
        return self._org_url
    #----------------------------------------------------------------------
    @property
    def proxy_url(self):
        """gets the proxy url"""
        return self._proxy_url
    #----------------------------------------------------------------------
    @proxy_url.setter
    def proxy_url(self, value):
        """ sets the proxy_url """
        self._proxy_url = value
    #----------------------------------------------------------------------
    @property
    def proxy_port(self):
        """ gets the proxy port """
        return self._proxy_port
    #----------------------------------------------------------------------
    @proxy_port.setter
    def proxy_port(self, value):
        """ sets the proxy port """
        if isinstance(value, int):
            self._proxy_port = value
    #----------------------------------------------------------------------
    @property
    def username(self):
        """ returns the username """
        return self._username
    #----------------------------------------------------------------------
    @username.setter
    def username(self, username):
        """ sets the username """
        self._token = None
        self._username = username
    #----------------------------------------------------------------------
    @property
    def password(self):
        """ returns **** for the password """
        return "****"
    #----------------------------------------------------------------------
    @password.setter
    def password(self, value):
        """ sets the password """
        self._token = None
        self._password = value
    #----------------------------------------------------------------------
    @property
    def token_url(self):
        """ returns the token url """
        return self._token_url
    #----------------------------------------------------------------------
    @token_url.setter
    def token_url(self, value):
        """ sets the token url """
        self._token = None
        self._token_url = value
    #----------------------------------------------------------------------
    @property
    def tokenExperationDate(self):
        """ returns when the token is not valid """
        return self._token_expires_on
    #----------------------------------------------------------------------
    @property
    def tokenObtainedDate(self):
        """ returns when the token was generated """
        return self._token_created_on
    #----------------------------------------------------------------------
    @property
    def referer_url(self):
        """ returns when the token was generated """
        return self._referer_url        
    #----------------------------------------------------------------------
    @property
    def token(self):
        """ returns the token for the site """
        if self._token is None or \
           datetime.datetime.now() >= self._token_expires_on:
            result = self._generateForTokenSecurity(username=self._username,
                                           password=self._password,
                                           tokenUrl=self._token_url)
            if 'error' in result:
                self._valid = False
                self._message = result
            else:
                self._valid = True
                self._message = "Token Generated"            
        return self._token
    #----------------------------------------------------------------------
    def servertoken(self,serverURL,referer):
        """ returns the server token for the server """
        if self._server_token is None or \
           datetime.datetime.now() >= self._server_token_expires_on or \
           self._server_url != serverURL:
            self._server_url = serverURL
            result = self._generateForServerTokenSecurity(serverURL=serverURL,
                                                          referer=referer,
                                                          token=self.token,
                                                          tokenUrl=self._token_url)
            if 'error' in result:
                self._valid = False
                self._message = result
            else:
                self._valid = True
                self._message = "Server Token Generated"            
        return self._server_token 
    
    #----------------------------------------------------------------------
    def _generateForServerTokenSecurity(self,
                                  serverURL,referer, token,tokenUrl,expiration=None):
        """ generates a token for a feature service """
        
        query_dict = {'serverURL':serverURL,
                      'token': token,
                      'f': 'json',
                      'request':'getToken',
                      'referer':referer}
        if expiration is not None:
            query_dict['expiration'] = expiration
        server_token = self._do_post(url=tokenUrl,
                              param_dict=query_dict,
                              proxy_port=self._proxy_port,
                              proxy_url=self._proxy_url)
        if 'error' in server_token:
            self._server_token = None
            self._server_token_created_on = None
            self._server_token_expires_on = None
            self._server_expires_in = None

            return server_token        
       
        else:
            self._server_token = server_token['token']
            self._server_token_created_on = datetime.datetime.now()
            if server_token['expires'] > 86400:
                seconds = 86400
            else:
                seconds = int(server_token['expires'])
            self._server_token_expires_on = self._token_created_on + datetime.timedelta(seconds=seconds)
            self._server_expires_in = server_token['expires']
            return server_token['token']

    #----------------------------------------------------------------------
    def _generateForTokenSecurity(self,
                                  username, password,
                                  tokenUrl, expiration=None):
        """ generates a token for a feature service """
        query_dict = {'username': username,
                      'password': password,
                      'client': 'requestip',
                      'f': 'json'}
        if expiration is not None:
            query_dict['expiration'] = expiration
        token = self._do_post(url=tokenUrl,
                              param_dict=query_dict,
                              proxy_port=self._proxy_port,
                              proxy_url=self._proxy_url)
        if 'error' in token:
            self._token = None
            self._token_created_on = None
            self._token_expires_on = None
            self._expires_in = None

            return token        
       
        else:
            self._token = token['token']
            self._token_created_on = datetime.datetime.now()
            if token['expires'] > 86400:
                seconds = 86400
            else:
                seconds = int(token['expires'])
            self._token_expires_on = self._token_created_on + datetime.timedelta(seconds=seconds)
            self._expires_in = token['expires']
            return token['token']

