from ..abstract_webtools import *
class urlManager:
    """
    urlManager is a class for managing URLs, including cleaning, validating, and finding the correct version.

    Args:
        url (str or None): The URL to manage (default is None).
        session (requests.Session): A custom requests session (default is the requests module's session).

    Attributes:
        session (requests.Session): The requests session used for making HTTP requests.
        clean_urls (list): List of cleaned URL variations.
        url (str): The current URL.
        protocol (str): The protocol part of the URL (e.g., "https").
        domain (str): The domain part of the URL (e.g., "example.com").
        path (str): The path part of the URL (e.g., "/path/to/resource").
        query (str): The query part of the URL (e.g., "?param=value").
        all_urls (list): List of all URLs (not used in the provided code).

    Methods:
        url_to_pieces(url): Split a URL into its protocol, domain, path, and query components.
        clean_url(url): Return a list of potential URL versions with and without 'www' and 'http(s)'.
        get_correct_url(url): Get the correct version of the URL from possible variations.
        update_url(url): Update the URL and related attributes.
        get_domain(url): Get the domain name from a URL.
        url_join(url, path): Join a base URL with a path.
        is_valid_url(url): Check if a URL is valid.
        make_valid(href, url): Make a URL valid by joining it with a base URL.
        get_relative_href(url, href): Get the relative href URL by joining it with a base URL.

    Note:
        - The urlManager class provides methods for managing URLs, including cleaning and validating them.
        - It also includes methods for joining and validating relative URLs.
    """

    def __init__(self, url=None, session=None):
        """
        Initialize a urlManager instance.

        Args:
            url (str or None): The URL to manage (default is None).
            session (requests.Session): A custom requests session (default is the requests module's session).
        """
        url = url or 'www.example.com'
        self._url=url
        self.url = url
        self.session= session or requests
        self.clean_urls = self.clean_url(url=url)
        self.url = self.get_correct_url(clean_urls=self.clean_urls)
        url_pieces = self.url_to_pieces(url=self.url)
        self.protocol,self.domain,self.path,self.query=url_pieces
        self.all_urls = []
    def url_to_pieces(self, url):
        
        try:
            match = re.match(r'^(https?)?://?([^/]+)(/[^?]+)?(\?.+)?', url)
            if match:
                protocol = match.group(1) if match.group(1) else None
                domain = match.group(2) if match.group(1) else None
                path = match.group(3) if match.group(3) else ""  # Handle None
                query = match.group(4) if match.group(4) else ""  # Handle None
        except:
            print(f'the url {url} was not reachable')
            protocol,domain,path,query=None,None,"",""
        return protocol, domain, path, query

    def clean_url(self,url=None) -> list:
        """
        Given a URL, return a list with potential URL versions including with and without 'www.', 
        and with 'http://' and 'https://'.
        """
        url = url or self.url 
        urls=[]
        if url:
            # Remove http:// or https:// prefix
            cleaned = url.replace("http://", "").replace("https://", "")
            no_subdomain = cleaned.replace("www.", "", 1)
            
            urls = [
                f"https://{cleaned}",
                f"http://{cleaned}",
            ]

            # Add variants without 'www' if it was present
            if cleaned != no_subdomain:
                urls.extend([
                    f"https://{no_subdomain}",
                    f"http://{no_subdomain}",
                ])

            # Add variants with 'www' if it wasn't present
            else:
                urls.extend([
                    f"https://www.{cleaned}",
                    f"http://www.{cleaned}",
                ])

        return urls

    def get_correct_url(self,url=None,clean_urls=None) -> (str or None):
        """
        Gets the correct URL from the possible variations by trying each one with an HTTP request.

        Args:
            url (str): The URL to find the correct version of.
            session (type(requests.Session), optional): The requests session to use for making HTTP requests.
                Defaults to requests.

        Returns:
            str: The correct version of the URL if found, or None if none of the variations are valid.
        """
        self.url = url
        if url==None and clean_urls != None:
            if self.url:
                url=self.url or clean_urls[0]
        if url!=None and clean_urls==None:
            clean_urls=self.clean_url(url)
        elif url==None and clean_urls==None:
            url=self.url
            clean_urls=self.clean_urls
        # Get the correct URL from the possible variations
        for url in clean_urls:
            try:
                source = self.session.get(url)
                return url
            except requests.exceptions.RequestException as e:
                print(e)
        return None
    def update_url(self,url):
        # These methods seem essential for setting up the urlManager object.
        self.url = url
        self.clean_urls = self.clean_url()
        self.correct_url = self.get_correct_url()
        self.url =self.correct_url
        self.protocol,self.domain,self.path,self.query=self.url_to_pieces(url=self.url)
        self.all_urls = []
    def get_domain(self,url=None):
        url = url or self.url 
        return urlparse(url).netloc
    def url_join(self,url,path):
        url = eatOuter(url,['/'])
        path = eatInner(path,['/'])
        slash=''
        if path[0] not in ['?','&']:
            slash = '/'
        url = url+slash+path
        return url
    @property
    def url(self):
        return self._url
    @url.setter
    def url(self, new_url):
        self._url = new_url
    def is_valid_url(self,url=None):
        """
        Check if the given URL is valid.
        """
        url = url or self.url 
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    def make_valid(self,href,url=None):
        def is_valid_url(url):
            url = url or self.url 
            """
            Check if the given URL is valid.
            """
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        if is_valid_url(href):
            return href
        new_link=urljoin(url,href)
        if is_valid_url(new_link):
            return new_link
        return False
    
    def get_relative_href(self,url,href):
        # join the URL if it's relative (not an absolute link)
        url = url or self.url 
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        return href
    def url_basename(self,url=None):
        url = url or self.url 
        path = urllib.parse.urlparse(url).path
        return path.strip('/').split('/')[-1]


    def base_url(self,url=None):
        url = url or self.url 
        return re.match(r'https?://[^?#]+/', url).group()


    def urljoin(self,base, path):
        if isinstance(path, bytes):
            path = path.decode()
        if not isinstance(path, str) or not path:
            return None
        if re.match(r'^(?:[a-zA-Z][a-zA-Z0-9+-.]*:)?//', path):
            return path
        if isinstance(base, bytes):
            base = base.decode()
        if not isinstance(base, str) or not re.match(
                r'^(?:https?:)?//', base):
            return None
        return urllib.parse.urljoin(base, path)
class urlManagerSingleton:
    _instance = None
    @staticmethod
    def get_instance(url=None,session=requests):
        if urlManagerSingleton._instance is None:
            urlManagerSingleton._instance = urlManager(url,session=session)
        elif urlManagerSingleton._instance.session != session or urlManagerSingleton._instance.url != url:
            urlManagerSingleton._instance = urlManager(url,session=session)
        return urlManagerSingleton._instance

def get_url(url=None,url_mgr=None):
    if not url and not url_mgr:
        return None
    if url:
        url_mgr = urlManager(url)
    return url_mgr.url
def get_url_mgr(url=None,url_mgr=None):
    if url_mgr == None and url:
         url_mgr = urlManager(url=url)
    if url_mgr and url == None:
        url = url_mgr.url
    return url_mgr 
