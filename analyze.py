import pickle
import os
from datetime import datetime
from matplotlib.dates import date2num
import matplotlib.pyplot as plt


# TIMELINES
# { "username": [list of tweets],
#    "username 2": [list of tweets]    
# }
TIMELINES = dict()
# NAMES
# list of user names
NAMES = set()

def get_tweet_timestamp(tid):
    """
    Get timestamp from tweet id
    """
    offset = 1288834974657
    tstamp = (tid >> 22) + offset
    return math.floor(tstamp/1000)

# Create list of usernames from twitter_users.txt
# Read user timelines into a dict {
# "username": list of Status objects from twitter module    
#}
with open("twitter_users.txt") as user_list:
    for line in user_list.readlines():
        name = line.rstrip("\n")
        NAMES.add(name)
        posts = []
        with open(f"serialized/{name}", "rb") as fd:
            while True:
                try:
                    posts.append(pickle.load(fd))
                except EOFError:
                    break
        TIMELINES[name] = posts


def retweets():
    """
    Parse twitter timelines into a list:
    [(user, retweeted_user), ...]
    """
    retweets = []
    for user, posts in TIMELINES.items():
        for post in posts:
            if post.retweeted_status and len(post.user_mentions) > 0:
                if post.user_mentions[0].screen_name in NAMES:
                    retweets.append((user, post.user_mentions[0].screen_name))
    return retweets


def replies():
    """
    Return list of replies parsed from user timelines
    [(tweeter, reply_target), ...]
    """
    replies = []
    for user, posts in TIMELINES.items():
        for post in posts:
            if post.in_reply_to_screen_name in NAMES and\
                    post.in_reply_to_screen_name != user:
                replies.append((user, post.in_reply_to_screen_name))
    return replies


def mentions():
    """
    return list of mentions parsed from user timelines
    [(tweeter, mentioned_user), ...]
    """
    mentions = []
    for user, posts in TIMELINES.items():
        for post in posts:
            for mention in post.user_mentions:
                append_mentions = mention.screen_name in NAMES and\
                    user != mention.screen_name
                if append_mentions:
                    mentions.append((user, mention.screen_name))
    return mentions


def posts_per_day():
    """
    Calculate posts per date from all user timelines
    return list of (timestamp, number of tweets) tuples
    """
    ppp = dict()
    for user, posts in TIMELINES.items():
        for post in posts:
            ts = get_tweet_timestamp(post.id)
            ts = date2num(datetime.fromtimestamp(ts).date())
            if ts not in ppp:
                ppp[ts] = 0
            ppp[ts] += 1
    plotlib_out = []
    for t, n in ppp.items():
        plotlib_out.append((t, n))
    return plotlib_out


def posts_per_day_user():
    """
    Calculate posts per date from user tweets
    return 
    { "username": list of (timestamp, number of tweets) tuples,
    ...
    }

    """
    pppu = dict()
    for user, posts in TIMELINES.items():
        for post in posts:
            ts = get_tweet_timestamp(post.id)
            ts = date2num(datetime.fromtimestamp(ts).date())
            if user not in pppu:
                pppu[user] = dict()
            if ts not in pppu[user]:
                pppu[user][ts] = 0
            pppu[user][ts] += 1
    plotlib_out = dict()
    for user, numposts in pppu.items():
        plotlib_out[user] = []
        for t, n in numposts.items():
            plotlib_out[user].append((t, n))
    return plotlib_out


def plot_dates(data, discrete=True):
    """
    Plot tweets per date in the collected dataset
    """
    data.sort()
    dates = [i[0] for i in data]
    vals = [i[1] for i in data]
    if discrete:
        plt.plot_date(dates, vals)
    else:
        plt.plot_date(dates, vals, "-")

    ext = "discrete" if discrete else "cont"
    locs, labels = plt.xticks()
    for label in labels:
        label.set_rotation(40)
        label.set_horizontalalignment('right')
    plt.tight_layout()
    plt.savefig(f"all_users_{ext}.svg")
    plt.clf()



def plot_dates_user(data, discrete=True):
    """
    Plot tweets per date for each individual user into a separate
    image
    """
    lims_x = lims_y = (9999999999999999999999999999, 0)
    if not os.path.exists("per_user_graphs"):
        os.mkdir("per_user_graphs")
    for user, pdata in data.items():
        x = (min([i[0] for i in pdata]),
             max([i[0] for i in pdata]))
        y = (0,
             max([i[1] for i in pdata]))
        lims_x = (min(lims_x[0], x[0]), max(lims_x[1], x[1]))
        lims_y = (0, max(lims_y[1], y[1]))
    for user, pdata in data.items():
        pdata.sort()
        dates = [i[0] for i in pdata]
        vals = [i[1] for i in pdata]
        if discrete:
            plt.plot_date(dates, vals, "o")
        else:
            plt.plot_date(dates, vals, "-")
        plt.xlim(lims_x)
        plt.ylim(lims_y)
        locs, labels = plt.xticks()
        for label in labels:
            label.set_rotation(40)
            label.set_horizontalalignment('right')
        plt.title(user)
        # plt.show()
        plt.tight_layout()

        ext = "discrete" if discrete else "cont"
        if not os.path.exists(f"per_user_graphs/{ext}"):
            os.mkdir(f"per_user_graphs/{ext}")
        plt.savefig(f"per_user_graphs/{ext}/{user}.svg")
        plt.clf()



RETWEETS = retweets() # [(retweeter, target),...]
MENTIONS = mentions() # [(tweeter, mention_target),...]
REPLIES = replies() # [(tweeter, reply_target),...]
POSTS_PER_DAY = posts_per_day()  # timestamp: number of tweets...
POSTS_PER_DAY_USER = posts_per_day_user()  # user: {timestamp: number of tweets...}

if __name__ == "__main__":
    plot_dates_user(POSTS_PER_DAY_USER)
    plot_dates_user(POSTS_PER_DAY_USER, False)
    plot_dates(POSTS_PER_DAY)
    plot_dates(POSTS_PER_DAY, False)