"""
=============================================================
  STEP 1 — GRAPH MODULE
  Build a Knowledge Graph using Semantica ContextGraph
=============================================================

What this script does:
  1. Creates a ContextGraph
  2. Adds entities (People, Companies, Concepts)
  3. Adds relationships between them
  4. Queries and explores the graph

Run:
    python examples/my_graph_demo.py
"""

import json
from pathlib import Path
from semantica.context import ContextGraph

# ─── Output folder ────────────────────────────────────────────
OUTPUT = Path(__file__).resolve().parent / "my_outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

print("=" * 55)
print("  STEP 1 — GRAPH MODULE: Knowledge Graph Builder")
print("=" * 55)


# ─────────────────────────────────────────────────────────────
# STEP 1A: Create the graph
# ─────────────────────────────────────────────────────────────
print("\n[1] Creating ContextGraph...")
graph = ContextGraph(
    advanced_analytics=True,
    centrality_analysis=True,
    community_detection=True,
)
print("    Graph created!")


# ─────────────────────────────────────────────────────────────
# STEP 1B: Add NODES (Entities)
#   Each node has:
#     - id         : unique name/identifier
#     - type       : category (Person, Company, Concept, Tool)
#     - properties : extra details (dictionary)
# ─────────────────────────────────────────────────────────────
print("\n[2] Adding Nodes (Entities)...")

graph.add_nodes([

    # --- PEOPLE ---
    {
        "id": "Alice",
        "type": "Person",
        "properties": {
            "role": "Data Scientist",
            "age": 30,
            "skills": ["Python", "ML", "Knowledge Graphs"]
        }
    },
    {
        "id": "Bob",
        "type": "Person",
        "properties": {
            "role": "Software Engineer",
            "age": 27,
            "skills": ["Python", "FastAPI", "Databases"]
        }
    },
    {
        "id": "Carol",
        "type": "Person",
        "properties": {
            "role": "Product Manager",
            "age": 33,
            "skills": ["Strategy", "Agile", "Roadmaps"]
        }
    },

    # --- COMPANIES ---
    {
        "id": "TechCorp",
        "type": "Company",
        "properties": {
            "industry": "Artificial Intelligence",
            "founded": 2015,
            "size": "Large (500+ employees)"
        }
    },
    {
        "id": "DataLabs",
        "type": "Company",
        "properties": {
            "industry": "Data Analytics",
            "founded": 2019,
            "size": "Startup (50 employees)"
        }
    },

    # --- PROJECTS ---
    {
        "id": "ProjectAI",
        "type": "Project",
        "properties": {
            "status": "Active",
            "domain": "Machine Learning",
            "budget": "500000"
        }
    },
    {
        "id": "ProjectGraph",
        "type": "Project",
        "properties": {
            "status": "Planning",
            "domain": "Knowledge Graphs",
            "budget": "200000"
        }
    },

    # --- CONCEPTS ---
    {
        "id": "KnowledgeGraph",
        "type": "Concept",
        "properties": {
            "description": "A graph-based knowledge representation system",
            "field": "Computer Science"
        }
    },
    {
        "id": "MachineLearning",
        "type": "Concept",
        "properties": {
            "description": "Algorithms that learn from data",
            "field": "Artificial Intelligence"
        }
    },

    # --- TOOLS ---
    {
        "id": "Semantica",
        "type": "Tool",
        "properties": {
            "version": "0.6.5",
            "license": "MIT",
            "language": "Python"
        }
    },
    {
        "id": "Neo4j",
        "type": "Tool",
        "properties": {
            "version": "5.0",
            "license": "Community",
            "language": "Java"
        }
    },
])

print("    Added 11 nodes: 3 People, 2 Companies, 2 Projects, 2 Concepts, 2 Tools")


# ─────────────────────────────────────────────────────────────
# STEP 1C: Add EDGES (Relationships)
#   Each edge has:
#     - source_id  : starting node
#     - target_id  : ending node
#     - type       : relationship label
# ─────────────────────────────────────────────────────────────
print("\n[3] Adding Edges (Relationships)...")

graph.add_edges([

    # People → Companies (who works where)
    {"source_id": "Alice", "target_id": "TechCorp",  "type": "works_at"},
    {"source_id": "Bob",   "target_id": "TechCorp",  "type": "works_at"},
    {"source_id": "Carol", "target_id": "DataLabs",  "type": "works_at"},

    # People → Projects (who works on what)
    {"source_id": "Alice", "target_id": "ProjectAI",    "type": "leads"},
    {"source_id": "Bob",   "target_id": "ProjectAI",    "type": "contributes_to"},
    {"source_id": "Carol", "target_id": "ProjectGraph", "type": "manages"},
    {"source_id": "Alice", "target_id": "ProjectGraph", "type": "advises"},

    # Companies → Projects (who owns what)
    {"source_id": "TechCorp", "target_id": "ProjectAI",    "type": "owns"},
    {"source_id": "DataLabs", "target_id": "ProjectGraph",  "type": "owns"},

    # Projects → Tools (what tools they use)
    {"source_id": "ProjectAI",    "target_id": "Semantica", "type": "uses"},
    {"source_id": "ProjectGraph", "target_id": "Semantica", "type": "uses"},
    {"source_id": "ProjectGraph", "target_id": "Neo4j",     "type": "uses"},

    # Projects → Concepts (what domains they cover)
    {"source_id": "ProjectAI",    "target_id": "MachineLearning", "type": "focuses_on"},
    {"source_id": "ProjectGraph", "target_id": "KnowledgeGraph",  "type": "focuses_on"},

    # People → Concepts (who researches what)
    {"source_id": "Alice", "target_id": "KnowledgeGraph",  "type": "researches"},
    {"source_id": "Alice", "target_id": "MachineLearning", "type": "researches"},

    # People → People (collaboration)
    {"source_id": "Alice", "target_id": "Bob",   "type": "collaborates_with"},
    {"source_id": "Alice", "target_id": "Carol", "type": "collaborates_with"},
])

print("    Added 18 edges (works_at, leads, owns, uses, researches, collaborates_with)")


# ─────────────────────────────────────────────────────────────
# STEP 1D: QUERY the graph — get stats and info
# ─────────────────────────────────────────────────────────────
print("\n[4] Querying the Graph...")

# Get overall stats
stats = graph.stats()
print(f"\n    Graph Statistics:")
print(f"      Total Nodes : {stats.get('node_count', '?')}")
print(f"      Total Edges : {stats.get('edge_count', '?')}")

# Get the full graph as dictionary
graph_dict = graph.to_dict()

# Show all nodes
nodes = graph_dict.get("nodes", [])
print(f"\n    All Nodes ({len(nodes)}):")
for node in nodes:
    nid   = node.get("id", node.get("node_id", "?"))
    ntype = node.get("type", "?")
    print(f"      [{ntype}] {nid}")

# Show all edges
edges = graph_dict.get("edges", [])
print(f"\n    All Edges ({len(edges)}):")
for edge in edges:
    src  = edge.get("source_id", edge.get("source", "?"))
    tgt  = edge.get("target_id", edge.get("target", "?"))
    rel  = edge.get("type", "?")
    print(f"      {src}  --[{rel}]-->  {tgt}")

# Filter: show only Person nodes
print(f"\n    People in the graph:")
for node in nodes:
    if node.get("type") == "Person":
        nid   = node.get("id", node.get("node_id", "?"))
        props = node.get("properties", {})
        print(f"      {nid} — {props.get('role', '?')}")

# Filter: show only 'leads' relationships
print(f"\n    Leadership relationships (leads):")
for edge in edges:
    if edge.get("type") == "leads":
        src = edge.get("source_id", edge.get("source", "?"))
        tgt = edge.get("target_id", edge.get("target", "?"))
        print(f"      {src} leads {tgt}")

# Filter: show only 'uses' relationships
print(f"\n    Tool usage relationships (uses):")
for edge in edges:
    if edge.get("type") == "uses":
        src = edge.get("source_id", edge.get("source", "?"))
        tgt = edge.get("target_id", edge.get("target", "?"))
        print(f"      {src} uses {tgt}")


# ─────────────────────────────────────────────────────────────
# STEP 1E: SAVE the graph to a file
# ─────────────────────────────────────────────────────────────
print("\n[5] Saving graph to file...")

output_file = OUTPUT / "graph_demo_output.json"
output_file.write_text(json.dumps(graph_dict, indent=2, ensure_ascii=True))

print(f"    Saved -> {output_file}")


# ─────────────────────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  DONE! Graph Module Complete")
print("=" * 55)
print(f"""
  Summary:
    Nodes added  : {stats.get('node_count', '?')}
    Edges added  : {stats.get('edge_count', '?')}
    Output file  : examples/my_outputs/graph_demo_output.json

  Next steps:
    - Import graph_demo_output.json into the Explorer UI
    - Open http://localhost:5173 and go to Import/Export
    - Upload the JSON file to visualize your graph!
""")
