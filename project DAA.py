import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import folium
import webbrowser
import os

def create_graph(edges):
    G = nx.Graph()
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    return G

def find_shortest_path(G, source, target):
    return nx.shortest_path(G, source=source, target=target, weight='weight')

def show_graph(G, path):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=12)
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2)
    plt.show()

def show_on_map(positions, path=None):
    if not positions:
        messagebox.showerror("Error", "No positions available to show the map.")
        return

    first = next(iter(positions.values()))
    m = folium.Map(location=first, zoom_start=14)

    for node, (lat, lon) in positions.items():
        folium.Marker(location=(lat, lon), popup=node).add_to(m)

    if path:
        points = [positions[n] for n in path if n in positions]
        folium.PolyLine(points, color="red", weight=5).add_to(m)

    map_file = "path_map.html"
    m.save(map_file)
    webbrowser.open("file://" + os.path.realpath(map_file))

def add_edge():
    u = entry_node1.get()
    v = entry_node2.get()
    try:
        w = float(entry_weight.get())

        if u and v and u != v:
            edges.append((u, v, w))
            nodes.update([u, v])

            # Automatically generate positions
            base_lat, base_lon = 36.75, 3.06  # Example: Algiers
            offset = 0.002 * len(positions)

            if u not in positions:
                positions[u] = (base_lat + offset, base_lon + offset)
            if v not in positions:
                positions[v] = (base_lat + offset + 0.001, base_lon + offset + 0.001)

            combo_source["values"] = list(nodes)
            combo_target["values"] = list(nodes)
            entry_node1.delete(0, tk.END)
            entry_node2.delete(0, tk.END)
            entry_weight.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Nodes must be different and not empty.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a numeric value for the weight.")

def compute_and_display():
    if not edges:
        messagebox.showerror("Error", "Please add some edges first.")
        return

    G = create_graph(edges)
    source = combo_source.get()
    target = combo_target.get()

    if source and target and source != target:
        try:
            path = find_shortest_path(G, source, target)
            result_label.config(text=f"Path: {' → '.join(path)}")
            show_graph(G, path)
            show_on_map(positions, path)
        except nx.NetworkXNoPath:
            messagebox.showwarning("No Path", f"No path found between {source} and {target}.")
    else:
        messagebox.showerror("Error", "Please select two different nodes.")

def display_map():
    if not edges:
        messagebox.showerror("Error", "Please add some edges first.")
        return
    G = create_graph(edges)
    source = combo_source.get()
    target = combo_target.get()
    path = []
    if source and target and source != target:
        try:
            path = find_shortest_path(G, source, target)
        except nx.NetworkXNoPath:
            messagebox.showwarning("No Path", f"No path found between {source} and {target}.")
    show_on_map(positions, path)

# Main GUI
root = tk.Tk()
root.title("Shortest Path Finder")
root.geometry("650x480")

edges = []
nodes = set()
positions = {}

tk.Label(root, text="Add an edge:").pack()
frame_add = tk.Frame(root)
frame_add.pack()

tk.Label(frame_add, text="Node 1:").grid(row=0, column=0)
entry_node1 = tk.Entry(frame_add)
entry_node1.grid(row=0, column=1)

tk.Label(frame_add, text="Node 2:").grid(row=0, column=2)
entry_node2 = tk.Entry(frame_add)
entry_node2.grid(row=0, column=3)

tk.Label(frame_add, text="Weight:").grid(row=0, column=4)
entry_weight = tk.Entry(frame_add)
entry_weight.grid(row=0, column=5)

tk.Button(frame_add, text="Add", command=add_edge).grid(row=0, column=6)

tk.Label(root, text="Source:").pack()
combo_source = ttk.Combobox(root, values=[])
combo_source.pack()

tk.Label(root, text="Target:").pack()
combo_target = ttk.Combobox(root, values=[])
combo_target.pack()

tk.Button(root, text="Find Shortest Path", command=compute_and_display).pack(pady=5)
tk.Button(root, text="Display on Map", command=display_map).pack(pady=5)

result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()
