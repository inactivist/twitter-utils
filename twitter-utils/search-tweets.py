"""
Query Twitter GET Search and dump values to stdout.
REF: https://dev.twitter.com/docs/api/1.1/get/search/tweets

Copyright (C) 2012 Michael Curry.  See LICENSE or COPYRIGHT files
for details.
"""
import sys
import os
import pprint
import argparse
import requests
import requests.auth
import simplejson as json

try:
    CACHE_NAME = __file__ + "-cache"
    # Use requests-cache if available.  We cache successful
    # requests for 1 minute, because requests_cache only supports
    # cache duration multiples of a minute...
    import requests_cache
    requests_cache.configure(cache_name=CACHE_NAME, expire_after=1)
except ImportError:
    pass

def twitter_oauth():
    """Return OAUTH authentication to be used in by requests library."""
    # Must supply twitter account credentials in environment variables.
    consumer_key = unicode(os.environ['CONSUMER_KEY'])
    consumer_secret = unicode(os.environ['CONSUMER_SECRET'])
    oauth_token = unicode(os.environ['ACCESS_KEY'])
    oauth_token_secret = unicode(os.environ['ACCESS_SECRET'])
    return requests.auth.OAuth1(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_token_secret,
        signature_type='auth_header')
    
# V1 search doesn't require auth.  V1.1 will.
# V1.1 search returns data that is more consistent with
# streaming and other APIs.
API_INFO = {
    "1":   { "url": "http://search.twitter.com/search.json" },
    "1.1": { "url": "https://api.twitter.com/1.1/search/tweets.json", "auth": twitter_oauth }
}

# Tuple of twitter search args and various attributes.
TWITTER_OPTS = (
    {'name': 'since_id'},
    {'name': 'max_id'},
    {'name': 'geocode'},
    {'name': 'lang'},
    {'name': 'locale'},
    {'name': 'result_type'},
    {'name': 'count', 'type': int}, # count not supported in 1.0 API.
    {'name': 'until' },
    {'name': 'include_entities', 'action': 'store_true', 'default': True },
    {'name': 'rpp', 'type': int}  # rpp is not supported in 1.1 API.
)

def hyphenize(name):
    """Convert underscores to hyphens."""
    return name.replace('_', '-')

def make_help_text(name):
    return 'The "%s" value.' % name

def api_version_type(value):
    if value not in API_INFO:
        raise argparse.ArgumentTypeError("must be one of %s" % API_INFO.keys())
    return value

def is_twitter_arg(name):
    """Return TRUE if name is a Twitter search argument."""
    return name in [x.get('name') for x in TWITTER_OPTS]


def get_opts():
    """Parse command line arguments and return them as argsparse options."""
    
    #
    # List of acceptable options.
    # If entry is a string, the argument is a string type representing the GET search API parameter name.
    # Otherwise, it's a dict with various parameters.
    parser = argparse.ArgumentParser(description="Query Twitter's GET Search API using Tweepy and output results as JSON strings.")
    # Program args
    my_args = parser.add_argument_group("Program options")
    my_args.add_argument("--api-version",
                         type=api_version_type,
                         default="1",
                         help="Twitter API version (default=1)",
                         metavar='version')
    
    # Twitter-specific args
    twitter_args = parser.add_argument_group('Twitter Search args')
    twitter_args.add_argument("q", help="The Get Search 'q' value.", metavar='query')
    
    for opt in TWITTER_OPTS:
        # 'name' is mandatory.
        name = opt['name']
        a = {
                'help': make_help_text(name),
            }
        if opt.get('default'): a['default'] = opt.get('default')
        if opt.get('type'): a['type'] = opt.get('type')
        if opt.get('action'): a['action'] = opt.get('action')
        # metavar is not allowed with action='store_true'
        if opt.get('action') != 'store_true': a['metavar'] = name
        # TODO: If API != "1", convert 'rpp' to 'count'
        # TODO: Deal with negation of --include-entities...
        twitter_args.add_argument("--%s" % hyphenize(name), **a)
    
    return parser.parse_args()

opts = get_opts()

# config = {'verbose': sys.stdout}
config = {}

# Get relevant parameters...
params = dict([v for v in vars(opts).iteritems() if v[1] is not None and is_twitter_arg(v[0])])
params['q'] = opts.q

request_args = {
    'params': params,
    'config': config
}

# Get the API-specific URL
url = API_INFO[opts.api_version]['url']

# Deal with auth if the API requires it...
auth_helper = API_INFO[opts.api_version].get('auth')
if callable(auth_helper):
    request_args['auth'] = auth_helper()
    
# Perform the search
response = requests.get(url, **request_args)
if response.status_code == 200:
    print response.text
else:
    sys.stderr.write('Error: %d' % response.status_code)

exit(response.status_code)
