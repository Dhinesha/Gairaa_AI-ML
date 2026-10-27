"""
=============================================================
  MY SEMANTICA IMPLEMENTATION  —  All 6 Core Modules
=============================================================

This script demonstrates all core Semantica modules:
  1. Graph Module         — Build a knowledge graph
  2. Entity Extraction    — Extract entities from text (NLP)
  3. Ontology Module      — Define and evaluate structure/rules
  4. Reasoning Module     — Logical inference (IF-THEN rules)
  5. Decision Intelligence— Track AI decisions + audit trail
  6. Export & Visualize   — Save results in multiple formats

Run:
    python examples/my_implementation.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


# -------------------------------------------------------------
# OUTPUT FOLDER  (all files saved here)
# -------------------------------------------------------------
OUTPUT_DIR = Path(__file__).resolve().parent / "my_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def separator(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# =============================================================
# MODULE 1 — GRAPH MODULE
# =============================================================
def run_graph_module():
    separator("MODULE 1: GRAPH MODULE")
    from semantica.context import ContextGraph

    graph = ContextGraph(advanced_analytics=True, centrality_analysis=True, community_detection=True)

    graph.add_nodes([
        {"id": "Alice",        "type": "Person",       "properties": {"role": "Data Scientist", "company": "TechCorp"}},
        {"id": "Bob",          "type": "Person",       "properties": {"role": "Engineer",       "company": "TechCorp"}},
        {"id": "TechCorp",     "type": "Organisation", "properties": {"industry": "AI",         "size": "Large"}},
        {"id": "ProjectAI",    "type": "Project",      "properties": {"status": "Active",       "domain": "Machine Learning"}},
        {"id": "KnowledgeGraph","type": "Concept",     "properties": {"description": "Graph-based knowledge representation"}},
        {"id": "Semantica",    "type": "Tool",         "properties": {"version": "0.6.5",       "type": "Open Source"}},
    ])

    graph.add_edges([
        {"source_id": "Alice",     "target_id": "TechCorp",        "type": "works_at"},
        {"source_id": "Bob",       "target_id": "TechCorp",        "type": "works_at"},
        {"source_id": "Alice",     "target_id": "ProjectAI",       "type": "leads"},
        {"source_id": "Bob",       "target_id": "ProjectAI",       "type": "contributes_to"},
        {"source_id": "ProjectAI", "target_id": "KnowledgeGraph",  "type": "uses"},
        {"source_id": "ProjectAI", "target_id": "Semantica",       "type": "powered_by"},
        {"source_id": "TechCorp",  "target_id": "ProjectAI",       "type": "owns"},
        {"source_id": "Alice",     "target_id": "KnowledgeGraph",  "type": "researches"},
    ])

    stats = graph.stats()
    print(f"\n  Graph built!  Nodes={stats.get('node_count','?')}  Edges={stats.get('edge_count','?')}")

    out = OUTPUT_DIR / "01_knowledge_graph.json"
    out.write_text(json.dumps(graph.to_dict(), indent=2, ensure_ascii=True))
    print(f"  Saved -> {out}")
    return graph


# =============================================================
# MODULE 2 — ENTITY EXTRACTION
# =============================================================
def run_entity_extraction():
    separator("MODULE 2: ENTITY EXTRACTION")
    from semantica.semantic_extract import (
        NamedEntityRecognizer, RelationExtractor, EventDetector,
        TripletExtractor, CoreferenceResolver, ExtractionValidator,
    )
    from semantica.normalize import clean_text, normalize_text

    raw_texts = [
        "Alice is a Data Scientist at TechCorp and she leads ProjectAI. "
        "TechCorp was founded in 2015 and is headquartered in New York. "
        "ProjectAI uses Semantica for building knowledge graphs.",
        "Bob joined TechCorp in 2021 as an Engineer. He contributes to ProjectAI "
        "and collaborates with Alice on machine learning pipelines. "
        "The project achieved a 40% efficiency improvement in Q3 2024.",
        "Semantica is an open-source framework for AI accountability. "
        "It provides context graphs, decision intelligence, and provenance tracking.",
    ]

    normalized = [normalize_text(clean_text(t)) for t in raw_texts]
    coref = CoreferenceResolver()
    resolved = [coref.resolve(t) for t in normalized]

    ner = NamedEntityRecognizer(method="pattern", confidence_threshold=0.2)
    entities_batch = ner.process_batch(resolved)
    all_entities = [e for batch in entities_batch for e in batch]

    rel_extractor = RelationExtractor(method="pattern", confidence_threshold=0.2)
    relations_batch = [rel_extractor.extract_relations(t, entities=e) for t, e in zip(resolved, entities_batch)]
    all_relations = [r for batch in relations_batch for r in batch]

    evt_detector = EventDetector()
    events_batch = [evt_detector.detect_events(t) for t in resolved]
    all_events = [ev for batch in events_batch for ev in batch]

    # Use extract_triplets per-text (process_batch has a known bug in fallback mode)
    triplet_extractor = TripletExtractor(method="pattern", include_provenance=True)
    all_triplets = []
    for text in resolved:
        try:
            triplets = triplet_extractor.extract_triplets(text)
            if isinstance(triplets, list):
                all_triplets.extend(triplets)
        except Exception:
            pass

    validator = ExtractionValidator()
    validator.validate_entities(all_entities)
    validator.validate_relations(all_relations)

    print(f"  Entities={len(all_entities)}  Relations={len(all_relations)}  Events={len(all_events)}  Triplets={len(all_triplets)}")

    out = OUTPUT_DIR / "02_extraction_results.json"
    out.write_text(json.dumps({
        "entities":  [{"text": str(getattr(e, "text", e)), "type": str(getattr(e, "label", getattr(e, "type", "entity")))} for e in all_entities[:20]],
        "relations": [{"subject": str(getattr(r, "subject", "?")), "predicate": str(getattr(r, "predicate", "?")), "object": str(getattr(r, "object", "?"))} for r in all_relations[:20]],
        "events":    [str(e) for e in all_events[:10]],
        "triplet_count": len(all_triplets),
    }, indent=2, ensure_ascii=True))
    print(f"  Saved -> {out}")
    return all_entities, all_relations


# =============================================================
# MODULE 3 — ONTOLOGY MODULE
# =============================================================
def run_ontology_module():
    separator("MODULE 3: ONTOLOGY MODULE")
    from semantica.ontology import OntologyEvaluator

    ontology_data = {
        "uri":   "https://example.org/techcorp-ontology",
        "label": "TechCorp Knowledge Ontology",
        "classes": [
            {"uri": "https://example.org/Person",       "name": "Person",       "label": "Person",       "description": "A human individual"},
            {"uri": "https://example.org/Organisation",  "name": "Organisation",  "label": "Organisation",  "description": "A company or org"},
            {"uri": "https://example.org/Project",       "name": "Project",       "label": "Project",       "description": "A project or initiative"},
            {"uri": "https://example.org/Concept",       "name": "Concept",       "label": "Concept",       "description": "An abstract concept"},
            {"uri": "https://example.org/Tool",          "name": "Tool",          "label": "Tool",          "description": "A software tool"},
            {"uri": "https://example.org/Decision",      "name": "Decision",      "label": "Decision",      "description": "A recorded AI decision"},
        ],
        "properties": [
            {"uri": "https://example.org/works_at",       "label": "works_at",       "domain": "Person",       "range": "Organisation"},
            {"uri": "https://example.org/leads",          "label": "leads",          "domain": "Person",       "range": "Project"},
            {"uri": "https://example.org/contributes_to", "label": "contributes_to", "domain": "Person",       "range": "Project"},
            {"uri": "https://example.org/uses",           "label": "uses",           "domain": "Project",      "range": "Tool"},
            {"uri": "https://example.org/owns",           "label": "owns",           "domain": "Organisation", "range": "Project"},
            {"uri": "https://example.org/researches",     "label": "researches",     "domain": "Person",       "range": "Concept"},
            {"uri": "https://example.org/powered_by",     "label": "powered_by",     "domain": "Project",      "range": "Tool"},
        ],
        "axioms": [
            "Person works_at exactly one Organisation",
            "All Decisions must have a confidence score",
        ],
    }

    evaluator = OntologyEvaluator()
    questions = [
        "Who works at TechCorp?",
        "Which projects does Alice lead?",
        "What tools does ProjectAI use?",
        "What decisions were made and by whom?",
        "How are concepts connected to people?",
    ]
    eval_result = evaluator.evaluate_ontology(ontology_data, competency_questions=questions)

    print(f"  Classes={len(ontology_data['classes'])}  Properties={len(ontology_data['properties'])}")
    if eval_result:
        print(f"  Coverage={getattr(eval_result,'coverage_score','N/A')}  Completeness={getattr(eval_result,'completeness_score','N/A')}")

    out = OUTPUT_DIR / "03_ontology_evaluation.json"
    out.write_text(json.dumps({
        "ontology": ontology_data,
        "competency_questions": questions,
        "evaluation": {"coverage_score": getattr(eval_result, "coverage_score", None), "completeness_score": getattr(eval_result, "completeness_score", None)},
    }, indent=2, ensure_ascii=True))
    print(f"  Saved -> {out}")
    return ontology_data


# =============================================================
# MODULE 4 — REASONING MODULE
# =============================================================
def run_reasoning_module():
    separator("MODULE 4: REASONING MODULE")
    from semantica.reasoning import Reasoner, ExplanationGenerator

    reasoner = Reasoner()
    reasoner.add_rule("IF WorksAt(?person, TechCorp) AND Leads(?person, ?project) THEN SeniorContributor(?person, ?project)")
    reasoner.add_rule("IF SeniorContributor(?person, ?project) AND ProjectUses(?project, Semantica) THEN SemanticaExpert(?person)")
    reasoner.add_rule("IF SemanticaExpert(?person) AND Researches(?person, KnowledgeGraph) THEN KGSpecialist(?person)")
    reasoner.add_rule("IF ProjectUses(?project, Semantica) AND OwnedBy(TechCorp, ?project) THEN TechCorpUsesSemantica(True)")

    reasoner.add_fact("WorksAt(Alice, TechCorp)")
    reasoner.add_fact("Leads(Alice, ProjectAI)")
    reasoner.add_fact("WorksAt(Bob, TechCorp)")
    reasoner.add_fact("ProjectUses(ProjectAI, Semantica)")
    reasoner.add_fact("OwnedBy(TechCorp, ProjectAI)")
    reasoner.add_fact("Researches(Alice, KnowledgeGraph)")

    inferred = reasoner.forward_chain()
    print(f"  Rules=4  Facts=6  Inferred={len(inferred)}")
    for f in inferred:
        print(f"    -> {f.conclusion}")

    explanation_text = ""
    if inferred:
        explanation = ExplanationGenerator().generate_explanation(inferred[-1])
        explanation_text = explanation.natural_language
        print(f"  Explanation: {explanation_text}")

    out = OUTPUT_DIR / "04_reasoning_results.json"
    out.write_text(json.dumps({
        "inferred_facts": [str(f.conclusion) for f in inferred],
        "explanation": explanation_text,
    }, indent=2, ensure_ascii=True))
    print(f"  Saved -> {out}")
    return inferred


# =============================================================
# MODULE 5 — DECISION INTELLIGENCE
# =============================================================
def run_decision_intelligence(graph):
    separator("MODULE 5: DECISION INTELLIGENCE")
    from semantica.context import AgentContext, Decision, PolicyEngine, Policy, multi_hop_query
    from semantica.vector_store import VectorStore
    from semantica.provenance import ProvenanceManager

    vector_store = VectorStore(backend="inmemory", dimension=384)
    agent = AgentContext(vector_store=vector_store, knowledge_graph=graph, decision_tracking=True, advanced_analytics=True)
    agent.store([
        {"content": "Alice is leading ProjectAI at TechCorp using Semantica.", "metadata": {"source": "hr_system"}},
        {"content": "ProjectAI achieved 40% efficiency gain in Q3 2024.",      "metadata": {"source": "report_q3"}},
        {"content": "TechCorp adopted Semantica for AI accountability.",        "metadata": {"source": "tech_blog"}},
    ], extract_entities=False, extract_relationships=False)

    agent.record_decision(category="project_approval", scenario="Should ProjectAI continue into Phase 2?",
        reasoning="40% efficiency gain, strategic alignment confirmed.", outcome="approved_for_phase2",
        confidence=0.95, entities=["Alice","ProjectAI","TechCorp"])
    print("  Decision 1 recorded: project_approval  (confidence=0.95)")

    agent.record_decision(category="tool_selection", scenario="Which framework for knowledge graphs?",
        reasoning="Semantica: open-source, W3C standards, self-hostable.", outcome="selected_semantica",
        confidence=0.88, entities=["ProjectAI","Semantica","KnowledgeGraph"])
    print("  Decision 2 recorded: tool_selection    (confidence=0.88)")

    policy_engine = PolicyEngine(graph)
    policy = Policy(
        policy_id="POL-001", name="Project Approval Policy",
        description="min confidence 0.80, valid category required.",
        rules={"min_confidence": 0.80, "required_categories": ["project_approval","tool_selection"],
               "allowed_outcomes": ["approved_for_phase2","selected_semantica","rejected"]},
        category="project_approval", version="1.0",
        created_at=datetime.now(), updated_at=datetime.now(), metadata={},
    )
    policy_engine.add_policy(policy)

    decision_obj = Decision(decision_id="", category="project_approval",
        scenario="Should ProjectAI continue into Phase 2?",
        reasoning="Strong Q3 performance and strategic alignment confirmed.",
        outcome="approved_for_phase2", confidence=0.95, timestamp=datetime.now(),
        decision_maker="ai_governance_agent", metadata={"reviewed_by": "Alice"})
    trace_id = graph.record_decision(
        category=decision_obj.category, scenario=decision_obj.scenario,
        reasoning=decision_obj.reasoning, outcome=decision_obj.outcome,
        confidence=decision_obj.confidence, entities=["Alice","ProjectAI"],
        decision_maker=decision_obj.decision_maker, metadata=decision_obj.metadata)

    compliance = policy_engine.check_compliance(decision_obj, "POL-001")
    print(f"  Compliance check: {compliance}")

    precedents = agent.find_precedents(scenario="AI tool selection for knowledge graph", category="tool_selection", limit=3, use_hybrid_search=True)
    print(f"  Precedents found: {len(precedents) if precedents else 0}")

    path = multi_hop_query(graph, start_entity="Alice", query="Trace Alice role in ProjectAI using Semantica", max_hops=3)
    print(f"  Multi-hop path  : {len(path) if path else 0} hops")

    graph.analyze_decision_impact(trace_id)

    prov = ProvenanceManager(storage_path=str(OUTPUT_DIR / "05_provenance.db"))
    prov.track_entity("Alice",     source="hr_system",  metadata={"role": "Data Scientist"})
    prov.track_entity("ProjectAI", source="pmo_system", metadata={"status": "Active"})
    prov.track_entity("Semantica", source="tech_blog",  metadata={"version": "0.6.5"})
    prov.track_relationship("alice_leads_projectai", source="org_chart", metadata={"type": "leads"})
    prov_stats = prov.get_statistics()
    print(f"  Provenance stats: {prov_stats}")

    out = OUTPUT_DIR / "05_decision_intelligence.json"
    out.write_text(json.dumps({
        "decisions_recorded":  graph.get_decision_summary().get("total_decisions", 0),
        "compliance_result":   str(compliance),
        "precedents_found":    len(precedents) if precedents else 0,
        "multi_hop_hops":      len(path) if path else 0,
        "provenance_stats":    prov_stats,
    }, indent=2, ensure_ascii=True))
    print(f"  Saved -> {out}")
    return graph


# =============================================================
# MODULE 6 — ANALYTICS + EXPORT + VISUALIZATION
# =============================================================
def run_export_and_analytics(graph):
    separator("MODULE 6: ANALYTICS + EXPORT + VISUALIZATION")
    from semantica.kg import GraphBuilder, GraphAnalyzer, CentralityCalculator, CommunityDetector, ConnectivityAnalyzer, LinkPredictor
    from semantica.export import export_json, export_rdf, export_yaml, export_graph, export_lpg, ReportGenerator
    from semantica.visualization import KGVisualizer

    graph_dict = graph.to_dict()
    builder = GraphBuilder(merge_entities=True, resolve_conflicts=True)
    kg = builder.build([{"entities": graph_dict.get("nodes", []), "relationships": graph_dict.get("edges", [])}], extract=False)

    centrality_data  = CentralityCalculator().calculate_all_centrality(kg)
    community_data   = CommunityDetector().detect_communities(kg, algorithm="louvain")
    connectivity_data= ConnectivityAnalyzer().analyze_connectivity(kg)
    predicted_links  = LinkPredictor().predict_links(kg, top_k=5)

    print(f"  KG entities={len(kg.get('entities',[]))}  relations={len(kg.get('relationships',[]))}")
    print(f"  Centrality keys: {list(centrality_data.keys())[:3]}")
    print(f"  Predicted links: {len(predicted_links) if predicted_links else 0}")

    export_json( kg, OUTPUT_DIR / "06_knowledge_graph.json",    format="json")
    export_rdf(  kg, OUTPUT_DIR / "06_knowledge_graph.ttl",     format="turtle")
    export_yaml( graph_dict, OUTPUT_DIR / "06_context_graph.yaml")
    export_graph(graph_dict, OUTPUT_DIR / "06_context_graph.graphml", format="graphml")
    export_lpg(  kg, OUTPUT_DIR / "06_knowledge_graph.cypher",  method="cypher")
    print("  Exported: JSON, RDF/Turtle, YAML, GraphML, Cypher")

    ReportGenerator(format="markdown", include_charts=False).generate_report(
        {"title": "TechCorp KG Report", "summary": {"nodes": len(graph_dict.get("nodes",[])), "edges": len(graph_dict.get("edges",[]))}},
        OUTPUT_DIR / "06_final_report.md", format="markdown")
    print("  Markdown report generated")

    try:
        KGVisualizer(layout="force", color_scheme="default").visualize_network(
            kg, output="html", file_path=OUTPUT_DIR / "06_graph_network.html")
        print(f"  HTML visualization -> {OUTPUT_DIR / '06_graph_network.html'}")
    except Exception as exc:
        print(f"  Visualization skipped: {exc}")

    out = OUTPUT_DIR / "06_analytics_summary.json"
    out.write_text(json.dumps({"centrality_keys": list(centrality_data.keys()), "predicted_links": len(predicted_links) if predicted_links else 0}, indent=2))
    print(f"  Saved -> {out}")


# =============================================================
# MAIN
# =============================================================
def main():
    print("\n" + "#" * 60)
    print("  SEMANTICA — FULL IMPLEMENTATION  (All 6 Modules)")
    print("#" * 60)
    print(f"  Output: {OUTPUT_DIR}\n")

    graph    = run_graph_module()
    entities, relations = run_entity_extraction()
    ontology = run_ontology_module()
    inferred = run_reasoning_module()
    graph    = run_decision_intelligence(graph)
    run_export_and_analytics(graph)

    separator("ALL DONE")
    print(f"  Output files in: {OUTPUT_DIR}")
    for f in sorted(OUTPUT_DIR.glob("*")):
        print(f"    {f.name}")
    print()


if __name__ == "__main__":
    main()
