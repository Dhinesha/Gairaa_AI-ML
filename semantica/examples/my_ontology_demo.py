"""
=============================================================
  STEP 3 — ONTOLOGY MODULE
  Define the Schema & Rules of your Knowledge Graph
=============================================================

What this script does:
  1. Defines an Ontology (Schema) for a Knowledge Graph
  2. Creates Classes (Node Types)
  3. Creates Properties (Edge Types & Attributes)
  4. Defines Axioms (Rules)
  5. Evaluates the Ontology against Competency Questions

Run:
    python examples/my_ontology_demo.py
"""

import json
from pathlib import Path
from semantica.ontology import OntologyEvaluator

# ─── Output folder ────────────────────────────────────────────
OUTPUT = Path(__file__).resolve().parent / "my_outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("  STEP 3 — ONTOLOGY MODULE: Define Schema")
print("=" * 60)


# ─────────────────────────────────────────────────────────────
# STEP 3A: Define the Ontology (Schema)
#   Think of this like a database schema, but for a graph.
#   It tells the system what types of nodes and edges are allowed.
# ─────────────────────────────────────────────────────────────
print("\n[1] Defining the Ontology Schema...")

ontology_data = {
    "uri":   "https://example.org/techcorp-ontology",
    "label": "TechCorp Knowledge Ontology",
    
    # ── CLASSES (Node Types) ──
    "classes": [
        {"uri": "https://example.org/Person",       "name": "Person",       "label": "Person",       "description": "A human individual"},
        {"uri": "https://example.org/Organisation", "name": "Organisation", "label": "Organisation", "description": "A company or organization"},
        {"uri": "https://example.org/Project",      "name": "Project",      "label": "Project",      "description": "A project or initiative"},
        {"uri": "https://example.org/Concept",      "name": "Concept",      "label": "Concept",      "description": "An abstract concept or domain"},
        {"uri": "https://example.org/Tool",         "name": "Tool",         "label": "Tool",         "description": "A software tool or framework"},
    ],
    
    # ── PROPERTIES (Edge Types) ──
    # Domain = Source Node Type  |  Range = Target Node Type
    "properties": [
        {"uri": "https://example.org/works_at",       "label": "works_at",       "domain": "Person",       "range": "Organisation"},
        {"uri": "https://example.org/leads",          "label": "leads",          "domain": "Person",       "range": "Project"},
        {"uri": "https://example.org/contributes_to", "label": "contributes_to", "domain": "Person",       "range": "Project"},
        {"uri": "https://example.org/uses",           "label": "uses",           "domain": "Project",      "range": "Tool"},
        {"uri": "https://example.org/owns",           "label": "owns",           "domain": "Organisation", "range": "Project"},
        {"uri": "https://example.org/researches",     "label": "researches",     "domain": "Person",       "range": "Concept"},
    ],
    
    # ── AXIOMS (Rules & Constraints) ──
    "axioms": [
        "Person works_at exactly one Organisation",
        "Project must be owned by an Organisation",
    ],
}

print(f"    Schema defined!")
print(f"      - {len(ontology_data['classes'])} Classes (Node Types)")
print(f"      - {len(ontology_data['properties'])} Properties (Edge Types)")
print(f"      - {len(ontology_data['axioms'])} Axioms (Rules)")


# ─────────────────────────────────────────────────────────────
# STEP 3B: Evaluate the Ontology
#   We use Competency Questions (CQ) to test if our schema
#   is good enough to answer the questions we care about.
# ─────────────────────────────────────────────────────────────
print("\n[2] Evaluating Ontology against Competency Questions...")

evaluator = OntologyEvaluator()

# Questions our graph SHOULD be able to answer
competency_questions = [
    "Who works at TechCorp?",
    "Which projects does Alice lead?",
    "What tools does ProjectAI use?",
    "How are concepts connected to people?",
]

for i, q in enumerate(competency_questions):
    print(f"    Q{i+1}: {q}")

# Run the evaluation
print("\n    Running evaluation... (this analyzes coverage)")
eval_result = evaluator.evaluate_ontology(
    ontology_data, 
    competency_questions=competency_questions
)

if eval_result:
    print(f"\n    Evaluation Results:")
    print(f"      Coverage Score     : {getattr(eval_result, 'coverage_score', 'N/A')}")
    print(f"      Completeness Score : {getattr(eval_result, 'completeness_score', 'N/A')}")
else:
    print("    Evaluation failed or returned no result.")


# ─────────────────────────────────────────────────────────────
# STEP 3C: Save the Ontology
# ─────────────────────────────────────────────────────────────
print("\n[3] Saving Ontology to file...")

out = OUTPUT / "step3_ontology.json"
out.write_text(json.dumps({
    "ontology": ontology_data,
    "competency_questions": competency_questions,
    "evaluation": {
        "coverage_score":     getattr(eval_result, "coverage_score",     None) if eval_result else None,
        "completeness_score": getattr(eval_result, "completeness_score", None) if eval_result else None,
    },
}, indent=2, ensure_ascii=True))

print(f"    Saved -> {out}")


# ─────────────────────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  DONE! Ontology Module Complete")
print("=" * 60)
print(f"""
  Summary:
    You defined a strict schema for your graph! 
    This prevents messy data (like a Tool 'working at' a Person).
    
  Output File:
    step3_ontology.json
""")
