import sys
import argparse
import simplejson as json
import utils

SHINGLE_SIZE = 4

def get_shingles(str, size):
    for i in range(0, len(str)-size+1):
        yield str[i:i+size]
        
def jaccard(set1, set2):
    x = len(set1.intersection(set2))
    y = len(set1.union(set2))
    return x / float(y)


parser = argparse.ArgumentParser(description="Find similar items in Twiter stream JSON data using Jaccard index.")
parser.add_argument('match', help="The text fragment to match.")
parser.add_argument('--min-similarity', default=0.5, type=float, help="The minimum similarity (0.0 to 1.0) for a match.  Default=0.5")
parser.add_argument('--shingle-size', default=4, type=int, help="The shingle size to use (default=4.)")
args = parser.parse_args()
print args
# TODO: Normalize text
oset = set(get_shingles(utils.normalize_tweet(args.match), args.shingle_size))

for line in sys.stdin:
    try:
        tweet = json.loads(line)
    except json.JSONDecodeError:
        continue
    text = utils.normalize_tweet(tweet['text'])
    # TODO: Normalize text
    tset = set(get_shingles(text, args.shingle_size))
    j = jaccard(oset, tset)
    if j >= args.min_similarity:
        print "%s: %0.08f %s" % (tweet['id_str'], j, text)
    