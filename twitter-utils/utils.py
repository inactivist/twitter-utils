"""
Extracted from sylvester.libs.twtter.py
TODO: Move to separate lib/module.
"""
from dateutil import tz
import re
import string

HERE = tz.tzlocal()
UTC = tz.gettz('UTC')
_PUNCTUATION_TRANS_STR = string.maketrans(string.punctuation, ' ' * len(string.punctuation))
_PUNCTUATION_TRANS_UNICODE = dict((ord(char), ord(' ')) for char in string.punctuation)

# Regex from http://regexadvice.com/forums/permalink/38428/38405/ShowThread.aspx#38405

_CASHTAG_RE = re.compile(r'\$(?P<sym>(?:[A-Z]{1,4}(?:\.[A-Z]{1,2})?))(?=\s|$)')


def tweet_localtime(tweet_time):
    """Return a tweet's UTC time as localtime."""
    # http://stackoverflow.com/a/4563487/1309774
    # TODO: What is the performance impact of this method?
    return tweet_time.replace(tzinfo=UTC).astimezone(HERE)


def _punctuation_to_space(text):
    # TODO: Would be nice if we could avoid the conditional check...
    if isinstance(text, str):
        return text.translate(_PUNCTUATION_TRANS_STR)
    elif isinstance(text, unicode):
        return text.translate(_PUNCTUATION_TRANS_UNICODE)
    else:
        raise ValueError('text must be str or unicode, type is %s' % type(text))


def _remove_urls(s):
    return re.sub(r'https?:\/\/.*', ' ', s)


def extract_cashtags(text):
    """Return a list of cashtags found in text.
    There may be duplicates in the results; passing the results to the
    collections.Counter constructor to count occurances."""
    return _CASHTAG_RE.findall(text)


def normalize_tweet(tweet_text):
    """
    Normalize a tweet's text.
    Convert to lower case
    Remove URLs since they will be mangled when we remove punctuation.
    Replace all punctuation with a space
    Convert multiple spaces to single space
    Remove leading and trailing spaces (trim)
    """
    s = tweet_text.lower()
    s = _remove_urls(s)
    s = _punctuation_to_space(s) # replace punctuation with a space
    s = re.sub("[\s]+", " ", s) # multiple spaces with single space
    return s.strip()

def extract_words(text, short_word_length=3):
    s = text.split()
    return [word for word in s if len(word) > short_word_length]

