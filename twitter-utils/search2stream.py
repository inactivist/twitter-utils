"""
Convert GET search (v1.1 or higher) from searchtweets.py to 'stream' format
as expected by twitter-streamer.  This means it will enumerate each item in
the incoming JSON object's 'statuses' list, and output each on a separate
line.
"""
import sys
import simplejson as json

for line in sys.stdin:
    try:
        o = json.loads(line)
    except json.JSONDecodeError:
        sys.stderr.write("Parse error: %s\n" % line)
        continue
    for s in o['statuses']:
        print json.dumps(s)