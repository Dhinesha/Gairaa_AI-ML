"""
=============================================================
  STEP 4 — REASONING MODULE
  Infer new facts using IF-THEN logic rules
=============================================================

What this script does:
  1. Initializes the Semantica Reasoner
  2. Adds business logic rules (IF -> THEN)
  3. Adds known facts to the system
  4. Runs Forward Chaining to automatically deduce NEW facts
  5. Explains the reasoning in plain English

Run:
    python examples/my_reasoning_demo.py
"""

import json
from pathlib import Path
from semantica.reasoning import Reasoner, ExplanationGenerator

# ─── Output folder ────────────────────────────────────────────
OUTPUT = Path(__file__).resolve().parent / "my_outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("  STEP 4 — REASONING MODULE: Logical Inference")
print("=" * 60)


# ─────────────────────────────────────────────────────────────
# STEP 4A: Initialize Reasoner and Add Rules
#   We teach the AI business logic using IF-THEN rules.
#   Variables start with '?' (e.g., ?person, ?project)
# ─────────────────────────────────────────────────────────────
print("\n[1] Teaching AI the rules (Business Logic)...")

reasoner = Reasoner()

# Rule 1: If someone works at TechCorp and leads a project, they are a SeniorContributor
reasoner.add_rule(
    "IF WorksAt(?person, TechCorp) AND Leads(?person, ?project) "
    "THEN SeniorContributor(?person, ?project)"
)
print("    Added Rule 1: WorksAt + Leads -> SeniorContributor")

# Rule 2: If a SeniorContributor works on a project that uses Semantica, they are a SemanticaExpert
reasoner.add_rule(
    "IF SeniorContributor(?person, ?project) AND ProjectUses(?project, Semantica) "
    "THEN SemanticaExpert(?person)"
)
print("    Added Rule 2: SeniorContributor + Uses Semantica -> SemanticaExpert")

# Rule 3: If a SemanticaExpert researches Knowledge Graphs, they are a KGSpecialist
reasoner.add_rule(
    "IF SemanticaExpert(?person) AND Researches(?person, KnowledgeGraph) "
    "THEN KGSpecialist(?person)"
)
print("    Added Rule 3: SemanticaExpert + Researches KG -> KGSpecialist")


# ─────────────────────────────────────────────────────────────
# STEP 4B: Add Known Base Facts
#   We tell the system what we ALREADY know for sure.
# ─────────────────────────────────────────────────────────────
print("\n[2] Feeding known facts into the system...")

reasoner.add_fact("WorksAt(Alice, TechCorp)")
reasoner.add_fact("Leads(Alice, ProjectAI)")
reasoner.add_fact("ProjectUses(ProjectAI, Semantica)")
reasoner.add_fact("Researches(Alice, KnowledgeGraph)")
reasoner.add_fact("WorksAt(Bob, TechCorp)")

print("    Added 5 known facts (e.g., Alice works at TechCorp, Alice leads ProjectAI...)")


# ─────────────────────────────────────────────────────────────
# STEP 4C: Run Forward Chaining Inference
#   The AI chains the facts and rules together to discover 
#   new things we never explicitly told it!
# ─────────────────────────────────────────────────────────────
print("\n[3] Running Forward Chaining Inference... (AI is thinking...)")

# Trigger the reasoning engine
inferred_facts = reasoner.forward_chain()

print(f"\n    [SUCCESS] The AI automatically discovered {len(inferred_facts)} NEW facts!")
for fact in inferred_facts:
    print(f"      -> {fact.conclusion}")


# ─────────────────────────────────────────────────────────────
# STEP 4D: Generate Natural Language Explanations
#   Ask the AI "WHY" it reached a specific conclusion.
# ─────────────────────────────────────────────────────────────
print("\n[4] Generating Plain English Explanations...")

explanation_text = ""
if inferred_facts:
    # Pick the last inferred fact to explain
    target_fact = inferred_facts[-1]
    
    # Generate human-readable explanation
    generator = ExplanationGenerator()
    explanation = generator.generate_explanation(target_fact)
    
    explanation_text = explanation.natural_language
    print(f"    Q: Why did you conclude '{target_fact.conclusion}'?")
    print(f"    A: {explanation_text}")


# ─────────────────────────────────────────────────────────────
# STEP 4E: Save Results
# ─────────────────────────────────────────────────────────────
print("\n[5] Saving Results...")

out = OUTPUT / "step4_reasoning_results.json"
out.write_text(json.dumps({
    "rules_applied": 3,
    "base_facts_given": 5,
    "new_facts_inferred": [str(f.conclusion) for f in inferred_facts],
    "explanation_example": explanation_text,
}, indent=2, ensure_ascii=True))

print(f"    Saved -> {out}")


# ─────────────────────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  DONE! Reasoning Module Complete")
print("=" * 60)
print(f"""
  Summary:
    You never explicitly said "Alice is a KGSpecialist". 
    But by giving the AI rules and base facts, it connected the 
    dots and discovered it automatically!
""")
