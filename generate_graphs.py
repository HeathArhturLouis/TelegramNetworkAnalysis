import datetime
import os

import pandas as pd
import re
import numpy as np

import networkx as nx
import matplotlib.pyplot as plt


def extract_urls(text):
    # define regular expression pattern for URLs
    url_pattern = re.compile(r"(?P<url>https?://[^\s]+)")

    # find all URLs in the given text
    urls = re.findall(url_pattern, text)

    # return the list of URLs
    return urls


def no_matches(array1, array2):
    return len(np.intersect1d(array1, array2))


def generate_url_and_user_nw(
    epochs,  # Epoch dictionary
    chats,  # Chats
    sample_data_path,  # Path to stored chat data
):
    user_nw = pd.DataFrame(columns=["Chat", "Epoch", "UserList", "URLList"])

    for epoch_name in epochs.keys():
        for chat in chats:
            with open(
                os.path.join(
                    sample_data_path, "chat_" + chat + "_epoch_" + epoch_name + ".csv"
                ),
                "r",
            ) as file:
                # Clear header
                file.readline()

                users = []
                urls = []

                for line in file:
                    line.rstrip()
                    attributes = line.split(",")
                    urls = urls + extract_urls(attributes[3])
                    users.append(attributes[1])

                new_data = {
                    "Chat": chat,
                    "Epoch": epoch_name,
                    "UserList": users,
                    "URLList": urls,
                }
                new_row = pd.DataFrame([new_data])

                # concatenate the original DataFrame with the new DataFrame
                user_nw = pd.concat([user_nw, new_row], ignore_index=True)

    no_chats = len(chats)

    user_network = {}
    url_network = {}
    # dict(zip(epochs.keys(),  [np.empty((no_chats, no_chats)) * len(epochs)]))
    # dict(zip(epochs.keys(),  [np.empty((no_chats, no_chats)) * len(epochs)]))

    # Non pythonic : could be better
    for epoch_name in epochs.keys():
        user_network[epoch_name] = np.empty((no_chats, no_chats))
        url_network[epoch_name] = np.empty((no_chats, no_chats))

    chat_counter_x = 0
    chat_counter_y = 0

    for epoch_name in epochs.keys():
        # Construct the two d array
        chat_counter_x = 0
        for chat_1 in chats:
            chat_counter_y = 0
            for chat_2 in chats:
                user_network[epoch_name][chat_counter_x][chat_counter_y] = no_matches(
                    list(
                        user_nw.loc[
                            (user_nw["Chat"] == chat_1)
                            & (user_nw["Epoch"] == epoch_name)
                        ]["UserList"]
                    ),
                    list(
                        user_nw.loc[
                            (user_nw["Chat"] == chat_2)
                            & (user_nw["Epoch"] == epoch_name)
                        ]["UserList"]
                    ),
                )
                url_network[epoch_name][chat_counter_x][chat_counter_y] = no_matches(
                    list(
                        user_nw.loc[
                            (user_nw["Chat"] == chat_1)
                            & (user_nw["Epoch"] == epoch_name)
                        ]["URLList"]
                    ),
                    list(
                        user_nw.loc[
                            (user_nw["Chat"] == chat_2)
                            & (user_nw["Epoch"] == epoch_name)
                        ]["URLList"]
                    ),
                )
                chat_counter_y += 1
            chat_counter_x += 1

    return {"URL": url_network, "UserID": user_network}


def construct_graph(
    adj_mat,  # Adjacency matrix with doubble type weights witch will be saved under weight attribute of connection
    channel_names,  # Array of names of channels (!in orginal order!)
    epoch_name,  # Name of the epoch
    epochs,  # Dict specifying epoch config
    sample_interval,  # Interval of each sample
    sample_no,  # number of equally spaced samples to use
    graph_type,  # Type of graph, should be one of URL, UserID or Topic
    graph_data_path,  # Directory where to store graph data
):
    assert graph_type in ["URL", "UserID", "Topic"]

    # Preprocess adjacency matrix

    # Remove diagonal entries
    for i in range(len(adj_mat)):
        adj_mat[i][i] = 0.0

    # Construct graph object
    graph = nx.Graph(adj_mat)

    # Set the connection strengths
    for i in range(len(adj_mat)):
        for j in range(i + 1, len(adj_mat)):
            if adj_mat[i][j] > 0.0:
                graph[i][j]["weight"] = adj_mat[i][j]

    # Set graph metadata
    graph.graph["epoch_name"] = epoch_name
    graph.graph["epoch_start"] = str(epochs[epoch_name][0])
    graph.graph["epoch_end"] = str(epochs[epoch_name][1])
    graph.graph["sample_interval"] = str(sample_interval)
    graph.graph["sample_no"] = sample_no
    graph.graph["graph_type"] = graph_type

    # Rename nodes to channel names
    c_name_mapping = {
        k: v for k, v in zip(list(range(len(channel_names))), channel_names)
    }

    # Add additional info instead
    graph = nx.relabel_nodes(graph, mapping=c_name_mapping, copy=True)

    # Add attributes to nodes instead of renaming
    # for i in range(len(channel_names)):
    #    graph.nodes[i]['channel_name'] = c_name_mapping[i]

    # Store graph object
    fname = os.path.join(graph_data_path, f"{graph_type}_graph_{epoch_name}.graphml")

    # Save Graph
    nx.write_graphml(graph, fname)


def plot_graphml(graph_file):
    """
    Simple testing function, likely unused
    """
    graph = nx.read_graphml(graph_file)

    pos = nx.spring_layout(graph)

    nx.draw(graph, pos, with_labels=True, font_weight="bold")

    labels = nx.get_edge_attributes(graph, "weight")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
    plt.show()
