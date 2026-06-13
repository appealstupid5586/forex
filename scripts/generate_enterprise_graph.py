from __future__ import annotations

from pathlib import Path

from enterprise_graph import EnterpriseGraphManager


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    graph_root = repo_root / "enterprise_graph"
    graph_root.mkdir(parents=True, exist_ok=True)

    graph_agent = EnterpriseGraphManager()
    graph_agent.populate_from_skills(repo_root / "skills")
    graph_agent.populate_from_imports(repo_root, skills_root="skills", backend_root="backend/app")

    json_path = graph_root / "enterprise_graph.json"
    mermaid_path = graph_root / "enterprise_graph.mermaid"
    dot_path = graph_root / "enterprise_graph.dot"

    graph_agent.save(json_path)
    mermaid_path.write_text(graph_agent.to_mermaid(), encoding="utf-8")
    dot_path.write_text(graph_agent.to_dot(), encoding="utf-8")

    print("Enterprise graph generated:")
    print(f"  JSON: {json_path}")
    print(f"  Mermaid: {mermaid_path}")
    print(f"  DOT: {dot_path}")
    print(f"  Nodes: {len(graph_agent.nodes)}, Edges: {len(graph_agent.edges)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
