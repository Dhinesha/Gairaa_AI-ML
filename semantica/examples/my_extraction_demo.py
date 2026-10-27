"""
=============================================================
  STEP 2 — ENTITY EXTRACTION & NLP PIPELINE
  Extract entities and relations from raw text automatically
=============================================================

What this script does:
  1. Takes raw text as input
  2. Cleans & normalizes the text
  3. Extracts: Named Entities (Person, Org, Location)
  4. Extracts: Relations between entities
  5. Extracts: Events from text
  6. Builds a Knowledge Graph from the extracted data
  7. Saves the result

Run:
    python examples/my_extraction_demo.py
"""

import json
from pathlib import Path

from semantica.semantic_extract import (
    NamedEntityRecognizer,   # finds People, Orgs, Locations
    RelationExtractor,       # finds WHO does WHAT to WHOM
    EventDetector,           # finds events that happened
    CoreferenceResolver,     # replaces "he/she/it" with real names
    ExtractionValidator,     # checks extraction quality
)
from semantica.normalize import clean_text, normalize_text
from semantica.kg import GraphBuilder
from semantica.export import export_json

# ─── Output folder ────────────────────────────────────────────
OUTPUT = Path(__file__).resolve().parent / "my_outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("  STEP 2 — ENTITY EXTRACTION & NLP")
print("=" * 60)


# ─────────────────────────────────────────────────────────────
# STEP 2A: Raw Text Input
#   This is the text we want to extract information from.
#   In real life this could come from:
#     - A PDF document
#     - A website
#     - A news article
#     - A database record
# ─────────────────────────────────────────────────────────────
print("\n[1] Raw Text Input...")

raw_texts = [
    # Text 1: Project Overview
    """
    Semantica transforms unstructured data into knowledge graphs.
    It adds a context and accountability layer on top of your existing AI stack like LangChain and LlamaIndex.
    The Knowledge Graph stores information as Nodes like people and companies, and Edges like works_for and founded_by.
    """,

    # Text 2: Extractors & Tools
    """
    The Entity Extraction (NER) module scans text to find and classify real-world entities.
    For example, Apple Inc. was founded by Steve Jobs in 1976 in Cupertino.
    The Relation Extraction finds how entities are connected.
    The tool uses NamedEntityRecognizer and RelationExtractor to process documents.
    """,

    # Text 3: Accountability & Origin
    """
    Provenance tracking is critical for AI accountability.
    Every answer can be traced back to the facts and relationships that produced it.
    The W3C PROV-O compliance makes every claim in your AI stack auditable.
    Semantica was created to ensure decision intelligence is explainable.
    """,
]

print(f"    Loaded {len(raw_texts)} text documents")
for i, t in enumerate(raw_texts):
    print(f"    Text {i+1}: {t.strip()[:60]}...")


# ─────────────────────────────────────────────────────────────
# STEP 2B: Clean & Normalize the Text
#   Remove noise, fix encoding, normalize whitespace
# ─────────────────────────────────────────────────────────────
print("\n[2] Cleaning & Normalizing Text...")

cleaned_texts = []
for text in raw_texts:
    cleaned   = clean_text(text, method="default")      # remove noise
    normalized = normalize_text(cleaned, method="default")  # fix format
    cleaned_texts.append(normalized)

print(f"    Cleaned {len(cleaned_texts)} texts")


# ─────────────────────────────────────────────────────────────
# STEP 2C: Coreference Resolution
#   Replace "he", "she", "it", "they" with real entity names
#   Example: "Alice works at TechCorp. She leads the project."
#            → "Alice works at TechCorp. Alice leads the project."
# ─────────────────────────────────────────────────────────────
print("\n[3] Resolving Coreferences (he/she/it -> real names)...")

coref = CoreferenceResolver()
resolved_texts = []
for text in cleaned_texts:
    resolved = coref.resolve(text)
    resolved_texts.append(resolved)

print(f"    Coreference resolution done for {len(resolved_texts)} texts")


# ─────────────────────────────────────────────────────────────
# STEP 2D: Named Entity Recognition (NER)
#   Find all real-world entities in the text:
#     - PERSON    : Alice Johnson, Dr. Sarah Williams
#     - ORG       : TechCorp, Harvard Medical Center
#     - LOCATION  : New York, London, Boston
#     - DATE      : 2024, January 2025
#     - CONCEPT   : Machine Learning, Alzheimer's
# ─────────────────────────────────────────────────────────────
print("\n[4] Extracting Named Entities (NER)...")

ner = NamedEntityRecognizer(
    method="pattern",
    confidence_threshold=0.2,   # accept entities with 20%+ confidence
)
entities_per_text = ner.process_batch(resolved_texts)
all_entities = [e for batch in entities_per_text for e in batch]

print(f"    Total entities found: {len(all_entities)}")
print(f"\n    Sample Entities:")
for entity in all_entities[:15]:
    text  = str(getattr(entity, "text",  getattr(entity, "id", str(entity))))
    label = str(getattr(entity, "label", getattr(entity, "type", "UNKNOWN")))
    score = getattr(entity, "confidence", getattr(entity, "score", None))
    score_str = f" (confidence: {score:.2f})" if score else ""
    print(f"      [{label}] {text}{score_str}")


# ─────────────────────────────────────────────────────────────
# STEP 2E: Relation Extraction
#   Find relationships between entities:
#     - Alice  WORKS_AT  TechCorp
#     - TechCorp  PARTNERED_WITH  DataLabs
#     - Dr. Sarah  PUBLISHED  Research
# ─────────────────────────────────────────────────────────────
print("\n[5] Extracting Relations between Entities...")

rel_extractor = RelationExtractor(
    method="pattern",
    confidence_threshold=0.2,
)
relations_per_text = [
    rel_extractor.extract_relations(text, entities=entities)
    for text, entities in zip(resolved_texts, entities_per_text)
]
all_relations = [r for batch in relations_per_text for r in batch]

print(f"    Total relations found: {len(all_relations)}")
print(f"\n    Sample Relations:")
for rel in all_relations[:10]:
    subj = str(getattr(rel, "subject",   getattr(rel, "source",    "?")))
    pred = str(getattr(rel, "predicate", getattr(rel, "type",      "?")))
    obj  = str(getattr(rel, "object",    getattr(rel, "target",    "?")))
    print(f"      {subj}  --[{pred}]-->  {obj}")


# ─────────────────────────────────────────────────────────────
# STEP 2F: Event Detection
#   Find events that happened in the text:
#     - Microsoft ACQUIRED OpenAI partnership
#     - Study PUBLISHED in January 2025
#     - Project ACHIEVED 40% improvement
# ─────────────────────────────────────────────────────────────
print("\n[6] Detecting Events...")

evt_detector = EventDetector()
events_per_text = [evt_detector.detect_events(t) for t in resolved_texts]
all_events = [ev for batch in events_per_text for ev in batch]

print(f"    Total events found: {len(all_events)}")
if all_events:
    print(f"    Sample Events:")
    for ev in all_events[:5]:
        print(f"      {str(ev)[:80]}")


# ─────────────────────────────────────────────────────────────
# STEP 2G: Validate the Extractions
#   Check if the extracted entities and relations are good quality
# ─────────────────────────────────────────────────────────────
print("\n[7] Validating Extractions...")

validator = ExtractionValidator()
entity_report   = validator.validate_entities(all_entities)
relation_report = validator.validate_relations(all_relations)

print(f"    Entity validation  : {str(entity_report)[:100]}")
print(f"    Relation validation: {str(relation_report)[:100]}")


# ─────────────────────────────────────────────────────────────
# STEP 2H: Build a Knowledge Graph from extracted data
#   Turn the extracted entities + relations into a real graph
# ─────────────────────────────────────────────────────────────
print("\n[8] Building Knowledge Graph from Extracted Data...")

builder = GraphBuilder(merge_entities=True, resolve_conflicts=True)
kg = builder.build(
    [{"entities": all_entities, "relationships": all_relations}],
    extract=False,
)

kg_entities      = kg.get("entities", [])
kg_relationships = kg.get("relationships", [])

print(f"    KG Nodes (entities)   : {len(kg_entities)}")
print(f"    KG Edges (relations)  : {len(kg_relationships)}")

if kg_entities:
    print(f"\n    Graph Nodes (first 10):")
    for node in kg_entities[:10]:
        nid   = node.get("id", "?")
        ntype = node.get("type", "?")
        print(f"      [{ntype}] {nid}")

if kg_relationships:
    print(f"\n    Graph Edges (first 10):")
    for edge in kg_relationships[:10]:
        src  = edge.get("source", edge.get("source_id", "?"))
        tgt  = edge.get("target", edge.get("target_id", "?"))
        rel  = edge.get("type", "?")
        print(f"      {src}  --[{rel}]-->  {tgt}")


# ─────────────────────────────────────────────────────────────
# STEP 2I: Save all results to files
# ─────────────────────────────────────────────────────────────
print("\n[9] Saving Results...")

# Save extracted entities & relations as JSON
extraction_output = {
    "summary": {
        "texts_processed":   len(raw_texts),
        "entities_found":    len(all_entities),
        "relations_found":   len(all_relations),
        "events_found":      len(all_events),
        "kg_nodes":          len(kg_entities),
        "kg_edges":          len(kg_relationships),
    },
    "entities": [
        {
            "text":  str(getattr(e, "text",  getattr(e, "id", str(e)))),
            "type":  str(getattr(e, "label", getattr(e, "type", "entity"))),
            "score": getattr(e, "confidence", getattr(e, "score", None)),
        }
        for e in all_entities
    ],
    "relations": [
        {
            "subject":   str(getattr(r, "subject",   getattr(r, "source", "?"))),
            "predicate": str(getattr(r, "predicate", getattr(r, "type",   "?"))),
            "object":    str(getattr(r, "object",    getattr(r, "target", "?"))),
        }
        for r in all_relations
    ],
    "events": [str(e) for e in all_events],
}

# Save extraction results
out1 = OUTPUT / "step2_extraction_results.json"
out1.write_text(json.dumps(extraction_output, indent=2, ensure_ascii=True))
print(f"    Extraction results -> {out1}")

# Save the Knowledge Graph (importable into Explorer UI!)
out2 = OUTPUT / "step2_nlp_knowledge_graph.json"
export_json(kg, out2, format="json")
print(f"    NLP Knowledge Graph -> {out2}")


# ─────────────────────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  DONE! Entity Extraction & NLP Complete")
print("=" * 60)
print(f"""
  What was extracted from {len(raw_texts)} text documents:
    Named Entities : {len(all_entities)}
    Relations      : {len(all_relations)}
    Events         : {len(all_events)}
    KG Nodes       : {len(kg_entities)}
    KG Edges       : {len(kg_relationships)}

  Output Files:
    step2_extraction_results.json  <- all entities & relations
    step2_nlp_knowledge_graph.json <- importable into Explorer UI

  Next Step:
    Import step2_nlp_knowledge_graph.json into the Explorer UI
    to visualize the graph built from your text!
""")
