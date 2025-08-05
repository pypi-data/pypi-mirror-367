import pandas as pd
import networkx as nx

"""
Graph Utilities for Data Vault Metadata
- Build a dependency graph from Excel metadata
- Support dbt-style selectors: +X, X+, @X
"""
def build_dependency_graph(excel_path):
    """
    Build a directed graph from the Excel metadata file.
    Nodes: All objects (stages, hubs, links, satellites, etc.)
    Edges: Parent-child relationships (e.g., satellites -> hubs/links, hub <- stage)
    Returns: networkx.DiGraph
    """
    xl = pd.ExcelFile(excel_path)
    G = nx.DiGraph()
    #DEBUG
    #print(xl.sheet_names, "\n", G)

    # Helper: add node with type
    def add_node(name, ntype, attrs=None):
        if attrs is None:
            attrs = {}
        G.add_node(name, type=ntype, **attrs)

    ### 1. Stage (new: must appear *before* Hubs and Links to ensure edges are built)
    # We'll try to build a stage for each hub and link.
    stages_added = set()
    if 'standard_hub' in xl.sheet_names:
        df = xl.parse('standard_hub')
        for _, row in df.iterrows():
            hub = row.get('Target_Hub_table_physical_name')
            if pd.notna(hub):
                stage_name = f"stg_{hub}"
                add_node(stage_name, 'stage', {"source_for": hub})
                stages_added.add((stage_name, hub))
    if 'standard_link' in xl.sheet_names:
        df = xl.parse('standard_link')
        for _, row in df.iterrows():
            link = row.get('Target_Link_table_physical_name')
            if pd.notna(link):
                stage_name = f"stg_{link}"
                add_node(stage_name, 'stage', {"source_for": link})
                stages_added.add((stage_name, link))

    ### 2. Hubs
    if 'standard_hub' in xl.sheet_names:
        df = xl.parse('standard_hub')
        for _, row in df.iterrows():
            hub = row.get('Target_Hub_table_physical_name')
            if pd.notna(hub):
                add_node(hub, 'hub', row.to_dict())
                # Connect stage to hub
                stage_name = f"stg_{hub}"
                if stage_name in G:
                    G.add_edge(stage_name, hub)

    ### 3. Links
    if 'standard_link' in xl.sheet_names:
        df = xl.parse('standard_link')
        for _, row in df.iterrows():
            link = row.get('Target_Link_table_physical_name')
            parent = row.get('Parent_Identifier') or row.get('Parent_Primary_Key_Physical_Name')
            if pd.notna(link):
                add_node(link, 'link', row.to_dict())
                # Link depends on parent hub(s)
                if pd.notna(parent):
                    G.add_edge(parent, link)
                # Connect stage to link
                stage_name = f"stg_{link}"
                if stage_name in G:
                    G.add_edge(stage_name, link)

    ### 4. Satellites
    if 'standard_satellite' in xl.sheet_names:
        df = xl.parse('standard_satellite')
        for _, row in df.iterrows():
            sat = row.get('Target_Satellite_Table_Physical_Name')
            parent = row.get('Parent_Identifier') or row.get('Parent_Primary_Key_Physical_Name')
            if pd.notna(sat):
                add_node(sat, 'satellite', row.to_dict())
                if pd.notna(parent):
                    G.add_edge(parent, sat)

    ### 5. Multi-Active Satellites
    if 'multiactive_satellite' in xl.sheet_names:
        df = xl.parse('multiactive_satellite')
        for _, row in df.iterrows():
            masat = row.get('Target_Satellite_Table_Physical_Name')
            parent = row.get('Parent_Identifier') or row.get('Parent_Primary_Key_Physical_Name')
            if pd.notna(masat):
                add_node(masat, 'ma_satellite', row.to_dict())
                if pd.notna(parent):
                    G.add_edge(parent, masat)

    ### 6. Non-Historized Satellites
    if 'non_historized_satellite' in xl.sheet_names:
        df = xl.parse('non_historized_satellite')
        for _, row in df.iterrows():
            nhsat = row.get('Target_Satellite_Table_Physical_Name')
            parent = row.get('Parent_Identifier') or row.get('Parent_Primary_Key_Physical_Name')
            if pd.notna(nhsat):
                add_node(nhsat, 'nh_satellite', row.to_dict())
                if pd.notna(parent):
                    G.add_edge(parent, nhsat)

    ### 7. Point-in-Time
    if 'pit' in xl.sheet_names:
        df = xl.parse('pit')
        for _, row in df.iterrows():
            pit = row.get('Pit_Physical_Table_Name')
            tracked = row.get('Tracked_Entity')
            if pd.notna(pit):
                add_node(pit, 'pit', row.to_dict())
                if pd.notna(tracked):
                    G.add_edge(tracked, pit)

    # Add more object types as needed...
    return G



def select_nodes(G, selectors):
    """
    Given a graph and a list of selectors (e.g., ['+A', 'B+', '@C']),
    return the set of selected nodes according to dbt-style selector logic.
    """
    selected = set()
    for sel in selectors:
        if sel.startswith('@'):
            node = sel[1:]
            if node in G:
                selected.add(node)
                selected.update(nx.ancestors(G, node))
                selected.update(nx.descendants(G, node))
        elif sel.endswith('+'):
            node = sel[:-1]
            if node in G:
                selected.add(node)
                selected.update(nx.descendants(G, node))
        elif sel.startswith('+'):
            node = sel[1:]
            if node in G:
                selected.add(node)
                selected.update(nx.ancestors(G, node))
        else:
            if sel in G:
                selected.add(sel)
    return selected


def print_graph(G):
    """
    Utility: Print the graph nodes and edges for debugging.
    """
    print("Nodes:")
    for n, d in G.nodes(data=True):
        print(f"  {n} ({d.get('type')})")
    print("Edges:")
    for u, v in G.edges():
        print(f"  {u} -> {v}") 