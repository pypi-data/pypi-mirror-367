import matplotlib.pyplot as plt
import networkx as nx

def print_nodes_and_edges(G):
    print("Nodes:", list(G.nodes()))
    print("Edges:", list(G.edges()))

def print_seccessors(G):
    for node in G.nodes():
        print(f"{node} -> {list(G.successors(node))}")

def print_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)  # możesz użyć też nx.kamada_kawai_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', arrowsize=20)
    plt.title("Your Data Vault Dependency Graph")
    plt.show()