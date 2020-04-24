import os
import sys
import twitter
import json
import pickle
import time
import math

from dotenv import load_dotenv

APRIL_20_2019 = 1555638322
OCT_20_2019 = 1571533200
MARCH_20_2020 = 1584666000
APRIL_20_2020 = 1587297600

START_TS = APRIL_20_2019
END_TS = APRIL_20_2020

SPIN = ["|", "/", "-", "\\"]


load_dotenv()
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

api = twitter.Api(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token_key= API_KEY,
    access_token_secret=API_SECRET
)

def get_tweet_timestamp(tid):
    """
    Get timestamp from tweet id
    """
    offset = 1288834974657
    tstamp = (tid >> 22) + offset
    return math.floor(tstamp/1000)

def ts_to_tid(tstamp):
    """
    Convert timestamp to timestamp-only tweet id
    """
    offset = 1288834974657
    return (tstamp*1000 - offset) << 22

with open("twitter_users.txt") as fd:
    twusers = [i.rstrip("\n") for i in fd.readlines()]

START = ts_to_tid(START_TS)
END = ts_to_tid(END_TS)

def get_tweets(user, end=END, end_ts=END_TS, start=START, start_ts=START_TS):
    all_tweets = []
    count = 0    
    if user == "realDonaldTrump":
        # Good old donald deserves more chances, because for some reason
        # the queries keep failing randomly
        try_treshold = 20
    else:
        try_treshold = 5
    with open(f"tweets/{user}.json", "w") as json_wfd, \
         open(f"serialized/{user}", "wb") as ser_wfd:
        
        tryagain_count = 0
        current = end_ts
        processing_count = 0
        while current > start_ts:
            try:
                processing_count += 1
                sys.stdout.write("\r"+ "[" + SPIN[processing_count%len(SPIN)] + "]" + f"[{user}] {count} tweets")
                tweets = api.GetUserTimeline(screen_name=user,
                                    since_id=start,
                                    max_id=ts_to_tid(current),
                                    count=200,
                                    include_rts=True,
                                    trim_user=True
                    )
                if not tweets:
                    tryagain_count += 1
                    if tryagain_count >= 3:
                        time.sleep(0.2)
                    if tryagain_count >= try_treshold:
                        if count < 5:
                            sys.stdout.write(f"\r[\u2717][{user}] No longer receiving tweets, something went wrong...\n")
                        break
                    continue
                tryagain_count = 0
                count += len(tweets)
                for tweet in tweets:
                    tweet_time = get_tweet_timestamp(tweet.id)
                    if tweet_time < current:
                        current = tweet_time
                    if tweet_time < start_ts:
                        continue
                    all_tweets.append(tweet.AsDict())
                    # Serialize twitter's Status-object, since they are pretty handy
                    pickle.dump(tweet, ser_wfd)
            except twitter.error.TwitterError as e:
                if e.message[0]["message"] == 'Rate limit exceeded':
                    sys.stdout.write(f"\r[\u23F2][{user}] Rate limit, waiting 18 minutes and trying again (Ctrl+C to abort)\n")
                    time.sleep(60*18)
                else:
                    sys.stdout.write(f"\r[\u2717][{user}] ERROR: {e.message}\n")
                    return user

        if not count:
            # no data, might as well not write the files
            os.remove(f"tweets/{user}.json")
            os.remove(f"serialized/{user}")
        sys.stdout.write(f"\r[\u2713][{user}] Got {count} tweets\n")
        json_wfd.write(json.dumps(all_tweets, indent=4))

def get_tweets_all():
    errors = []
    for user in twusers:
        # Do not overwrite existing data
        if os.path.exists(f"tweets/{user}.json") or \
           os.path.exists(f"serialized/{user}"):
            continue
        err = get_tweets(user)
        if err:
            errors.append(err)
    if errors: sys.stdout.write(f"\rList of incomplete queries: {errors}\n")

if __name__=="__main__":
    if not os.path.exists("tweets"):
        os.mkdir("tweets")
    if not os.path.exists("serialized"):
        os.mkdir("serialized")
    get_tweets_all()
    sys.stdout.write("\rAll done!\n")