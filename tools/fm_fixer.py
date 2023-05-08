import config
from generate_graphs import plot_graphml
import os
import networkx as nx
import csv

'''
Helper script to convert grphml files to csv
'''

path = config.graph_data_path
opath = os.path.join(config.graph_data_path, "Visione/")

graph_files = os.listdir(path)

graph_files = [a for a in graph_files if ".graphml" in a]


for file in graph_files:
    graph = nx.read_graphml(os.path.join(path, file))

    print(os.path.join(opath, file + ".csv"))
    with open(os.path.join(opath, file + ".csv"), "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Source", "Target", "Weight"])

        for u, v, data in graph.edges(data=True):
            weight = data.get("weight", 1)
            writer.writerow([u, v, weight])

        csvfile.close()
