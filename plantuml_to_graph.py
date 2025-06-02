import re
import sys
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

def parse_plantuml_to_graph(plantuml_text):
    """
    Parse a PlantUML component diagram into a directed NetworkX graph.

    Parameters:
    - plantuml_text (str): The PlantUML content as a single string.

    Returns:
    - G (networkx.DiGraph): Graph where nodes are component aliases, and edges
      represent directed connections.
    """
    # Regular expressions for parsing
    database_pattern = re.compile(r'database\s*"(?P<label>[^"]+)"\s+as\s+(?P<alias>\w+)', re.IGNORECASE)
    node_pattern = re.compile(r'\[\s*(?P<label>[^\]]+?)\s*\]\s*(?:as\s*(?P<alias>\w+))?')
    edge_pattern = re.compile(r'(?P<src>\w+)\s*-->\s*(?P<dst>\w+)')

    # Dictionaries to keep track of nodes and their labels
    alias_to_label = {}
    G = nx.DiGraph()

    for line in plantuml_text.splitlines():
        line = line.strip()
        
        # Skip empty lines and PlantUML directives
        if not line or line.startswith('@') or line.startswith('package') or line.startswith('!'):
            continue

                # Check for database definitions first
        db_match = database_pattern.search(line)
        if db_match:
            label = db_match.group('label').strip()
            alias = db_match.group('alias').strip()
            alias_to_label[alias] = label
            G.add_node(alias, label=label)
            continue

        # Check for node definitions
        node_match = node_pattern.search(line)
        if node_match:
            label = node_match.group('label').strip()
            alias = node_match.group('alias')
            if alias:
                node_id = alias
            else:
                # If no alias given, use a sanitized version of the label as node ID
                node_id = re.sub(r'\W+', '_', label).strip('_')

            # Add node with label as an attribute
            alias_to_label[node_id] = label
            G.add_node(node_id, label=label)
        
        # Check for edge definitions
        edge_match = edge_pattern.search(line)
        if edge_match:
            src = edge_match.group('src')
            dst = edge_match.group('dst')
            # Only add edge if both nodes exist (ignore otherwise)
            if src in G.nodes and dst in G.nodes:
                G.add_edge(src, dst)

    return G

def main():
    if len(sys.argv) != 3:
        print("Usage: python plantuml_to_graph_edit_distance.py <baseline_file.puml> <generated_file.puml>")
        sys.exit(1)

    baseline_file = sys.argv[1]
    generated_file = sys.argv[2]

    try:
        with open(baseline_file, 'r', encoding='utf-8') as f1, open(generated_file, 'r', encoding='utf-8') as f2:
            baseline_content = f1.read()
            generated_content = f2.read()
    except IOError as e:
        print(f"Error: Could not read file - {e}")
        sys.exit(1)

    # Parse PlantUML diagrams into graphs
    G_baseline = parse_plantuml_to_graph(baseline_content)
    G_generated = parse_plantuml_to_graph(generated_content)

    # Compute graph edit distance
    # Note: For larger graphs, this can be slow. For small to medium diagrams, it's manageable.
    try:
        matcher = categorical_node_match("label", None)
        ged = nx.graph_edit_distance(G_baseline, G_generated, node_match=matcher, timeout=180.0)
    except Exception as e:
        print(f"Error computing edit distance: {e}")
        sys.exit(1)

    print(f"Graph Edit Distance between diagrams: {ged}")

if __name__ == "__main__":
    main()

