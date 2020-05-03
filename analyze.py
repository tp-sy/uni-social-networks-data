import pickle
import os
import math
import numpy as np
from datetime import datetime
from matplotlib.dates import date2num
import matplotlib.pyplot as plt
import networkx as nx

# TIMELINES
# { "username": [list of tweets],
#   "username 2": [list of tweets]    
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


def calc_big_comp(graph, directed=True, multi=True):
    """
    Get a graph from the biggest component in the graph (one with most
    connected nodes)
    """
    big_nodes = max(nx.weakly_connected_components(graph), key=len)
    big_edges = []
    for e in graph.edges():
        if e[0] in big_nodes:
            big_edges.append(e)
    if directed and multi:
        classn = nx.MultiDiGraph
    elif directed:
        classn = nx.DiGraph
    elif multi:
        classn = nx.MultiGraph
    else:
        classn = nx.Graph
    return nxgraph(big_nodes, big_edges, classn)


def calc_shortest_paths(g):
    """
    Calculate average and variance for shortest path length for graph
    """
    patlens = list()
    read_paths = list()
    for n, paths in dict(nx.shortest_path_length(g)).items():
        for nt, l in paths.items():
            if nt != n:
                patlens.append(l)
    variance = variance = np.var(patlens)
    return sum(patlens)/len(patlens), variance


def calc_in_degree_centrality(graph):
    """
    Calculate average and variance for in-degree centrality
    """
    in_deg = nx.in_degree_centrality(graph)
    average = 0
    variance = 0
    total = 0
    for node, c in in_deg.items():
        total += c
    average = total/len(in_deg)
    variance = np.var([i for _, i in in_deg.items()])
    return average, variance


def calc_closeness_centrality(g):
    """
    Calculate average and variance for closeness centrality for graph
    """
    closeness = nx.closeness_centrality(g)
    c_vals = [c for _, c in closeness.items()]
    avg = sum(c_vals)/len(c_vals)
    var = np.var(c_vals)
    return avg, var


def calc_betweenness_centrality(g):
    """
    Calculate average and variance for closeness centrality for graph
    """
    betweenness = nx.betweenness_centrality(g)
    b_vals = [b for _, b in betweenness.items()]
    avg = sum(b_vals)/len(b_vals)
    var = np.var(b_vals)
    return avg, var


def calc_out_degree_centrality(graph):
    """
    Calculate average and variance for out-degree centrality
    """
    out_deg = nx.out_degree_centrality(graph)
    average = 0
    variance = 0
    total = 0
    for node, c in out_deg.items():
        total += c
    average = total/len(out_deg)
    variance = np.var([i for _, i in out_deg.items()])
    return average, variance


def in_degree_distribution(g):
    degrees = dict(g.in_degree())
    return [d for _, d in degrees.items()]


def out_degree_distribution(g):
    degrees = dict(g.out_degree())
    return [d for _, d in degrees.items()]


def degree_pairs(dg):
    dgd = dict()
    for n in dg:
        if n not in dgd:
            dgd[n] = dg.count(n)
    return [(j,i) for i,j in dgd.items()]


def plot_in_degree_distribution(g):
    """
    Call "plt.show()" or "plt.savefig()" after calling this function
    """
    dg = degree_pairs(in_degree_distribution(g))
    plt.clf()
    plt.xscale("log")
    plt.yscale("log")
    plt.scatter(*zip(*dg))


def plot_out_degree_distribution(g):
    """
    Call "plt.show()" or "plt.savefig()" after calling this function
    """
    dg = degree_pairs(out_degree_distribution(g))
    plt.clf()
    plt.xscale("log")
    plt.yscale("log")
    plt.scatter(*zip(*dg))
		
		
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

def tweet_in_links():
    res = dict()
    for u, posts in TIMELINES.items():
        for post in posts:
            if post.id not in res:
                res[post.id] = 0
            res[post.id] += 1
    finalres = dict()
    for pid, num in res.items():
        if num > 0:
            finalres[pid] = num
    return finalres


def date_from_tid(tid):
    ts = get_tweet_timestamp(tid)
    return date2num(datetime.fromtimestamp(ts).date())


def in_links_per_day_user(tuser):
    perday = dict()
    for user, posts in TIMELINES.items():
        if user == tuser:
            continue
        for post in posts:
            if tuser in [n.screen_name for n in post.user_mentions]:
                post_date = date_from_tid(post.id)
                if post_date not in perday:
                    perday[post_date] = 0
                perday[post_date] += 1
    return [(i,j) for i,j in perday.items()]


def in_links_all_users():
    if not os.path.exists("temporal"):
        os.mkdir("temporal")
    for u in NAMES:
        inlinks = in_links_per_day_user(u)
        dates = [i[0] for i in inlinks]
        posts = [i[1] for i in inlinks]
        print(inlinks)
        plt.clf()
        plt.xscale("log")
        plt.yscale("log")
        plt.plot_date(dates, posts, "o")
        plt.savefig(f"temporal/{u}.svg")

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

def calc_big_comp(graph, directed=True, multi=True):
    """
    Get a graph from the biggest component in the graph (one with most
    connected nodes)
    """
    big_nodes = max(nx.weakly_connected_components(graph), key=len)
    big_edges = []
    for e in graph.edges():
        if e[0] in big_nodes:
            big_edges.append(e)
    if directed and multi:
        classn = nx.MultiDiGraph
    elif directed:
        classn = nx.DiGraph
    elif multi:
        classn = nx.MultiGraph
    else:
        classn = nx.Graph
    return nxgraph(big_nodes, big_edges, classn)


def calc_shortest_paths(g):
    """
    Calculate average and variance for shortest path length for graph
    """
    patlens = list()
    read_paths = list()
    for n, paths in dict(nx.shortest_path_length(g)).items():
        for nt, l in paths.items():
            if nt != n:
                patlens.append(l)
    variance = variance = np.var(patlens)
    return sum(patlens)/len(patlens), variance


def calc_in_degree_centrality(graph):
    """
    Calculate average and variance for in-degree centrality
    """
    in_deg = nx.in_degree_centrality(graph)
    average = 0
    variance = 0
    total = 0
    for node, c in in_deg.items():
        total += c
    average = total/len(in_deg)
    variance = np.var([i for _, i in in_deg.items()])
    return average, variance


def calc_closeness_centrality(g):
    """
    Calculate average and variance for closeness centrality for graph
    """
    closeness = nx.closeness_centrality(g)
    c_vals = [c for _, c in closeness.items()]
    avg = sum(c_vals)/len(c_vals)
    var = np.var(c_vals)
    return avg, var


def calc_betweenness_centrality(g):
    """
    Calculate average and variance for closeness centrality for graph
    """
    betweenness = nx.betweenness_centrality(g)
    b_vals = [b for _, b in betweenness.items()]
    avg = sum(b_vals)/len(b_vals)
    var = np.var(b_vals)
    return avg, var


def calc_out_degree_centrality(graph):
    """
    Calculate average and variance for out-degree centrality
    """
    out_deg = nx.out_degree_centrality(graph)
    average = 0
    variance = 0
    total = 0
    for node, c in out_deg.items():
        total += c
    average = total/len(out_deg)
    variance = np.var([i for _, i in out_deg.items()])
    return average, variance


def in_degree_distribution(g):
    degrees = dict(g.in_degree())
    return [d for _, d in degrees.items()]


def out_degree_distribution(g):
    degrees = dict(g.out_degree())
    return [d for _, d in degrees.items()]


def degree_pairs(dg):
    dgd = dict()
    for n in dg:
        if n not in dgd:
            dgd[n] = dg.count(n)
    return [(j,i) for i,j in dgd.items()]


def plot_in_degree_distribution(g):
    """
    Call "plt.show()" or "plt.savefig()" after calling this function
    """
    dg = degree_pairs(in_degree_distribution(g))
    plt.clf()
    plt.xscale("log")
    plt.yscale("log")
    plt.scatter(*zip(*dg))


def plot_out_degree_distribution(g):
    """
    Call "plt.show()" or "plt.savefig()" after calling this function
    """
    dg = degree_pairs(out_degree_distribution(g))
    plt.clf()
    plt.xscale("log")
    plt.yscale("log")
    plt.scatter(*zip(*dg))

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


def nxgraph(nodes, edges, graph_class):
    g = graph_class()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    return g

def dir_graph(nodes=NAMES, edges=MENTIONS):
    """
    Create directed networkx graph
    """
    return nxgraph(nodes, edges, nx.DiGraph)

def graph(nodes=NAMES, edges=MENTIONS):
    """
    Create non-directed graph
    """
    return nxgraph(nodes, edges, nx.graph)

def mgraph(nodes=NAMES, edges=MENTIONS):
    """
    Create a graph where each edge is separate
    """
    return nxgraph(nodes, edges, nx.MultiGraph)

def dir_mgraph(nodes=NAMES, edges=MENTIONS):
    """
    Create a graph where each edge is directed and separate
    """
    return nxgraph(nodes, edges, nx.MultiDiGraph)

if __name__ == "__main__":
    plot_dates_user(POSTS_PER_DAY_USER)
    plot_dates_user(POSTS_PER_DAY_USER, False)
    plot_dates(POSTS_PER_DAY)
    plot_dates(POSTS_PER_DAY, False)