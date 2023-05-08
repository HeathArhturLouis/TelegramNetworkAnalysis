import generate_graphs
import config
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
import train_model

from bertopic import BERTopic


model = BERTopic.load("Data/Models/BERTopic_tSVD_14_4_23_100topics")

print(len(model.get_topics().keys()))

"""
for line in  train_model.batched_lines(os.path.join(config.raw_data_path, '_all.csv'), 10):
    print(line)
    break

"""


"""
with open(os.path.join(config.chat_data_path, "ActiveChats2023-04-03.csv") , "r") as file:
    # Discard cname
    file.readline()
    ch_names = [name.rstrip() for name in file]

adjacency_matrixes = generate_graphs.generate_url_and_user_nw(
            config.epochs,
            ch_names,
            config.raw_data_path
        )

adj_mat = adjacency_matrixes['URL']['Epoch 1']

for i in range(len(adj_mat)):
    adj_mat[i][i] = 0.0
    
# Construct graph object
graph = nx.Graph(adj_mat)

# Set the connection strengths
for i in range(len(adj_mat)):
    for j in range(i+1, len(adj_mat)):
        if adj_mat[i][j] > 0.0:
            graph[i][j]['weight'] = adj_mat[i][j]


c_name_mapping =  {k: v for k, v in zip( list(range(len(ch_names))), ch_names)}

for i in range(len(ch_names)):
    graph.nodes[i]['channel_name'] = c_name_mapping[i]


pos = nx.spring_layout(graph)

nx.draw(graph, pos, with_labels=True, font_weight='bold')

labels = nx.get_edge_attributes(graph, 'weight')
nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
plt.show()

"""
