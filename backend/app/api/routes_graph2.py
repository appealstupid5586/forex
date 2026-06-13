from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Query, Response
from typing import Optional

from app.core.config import get_settings
from enterprise_graph import EnterpriseGraphManager

settings = get_settings()
router = APIRouter(prefix="/api/v1/graph", tags=["enterprise_graph"])

# in-memory singleton for simple usage
graph_agent = EnterpriseGraphManager()

DEFAULT_STORE_PATH = settings.graph_path


@router.get("/status")
def graph_status():
    return {"ok": True, "nodes": len(graph_agent.nodes), "edges": len(graph_agent.edges)}


@router.post("/register/{node_id}")
def register_node(node_id: str):
    graph_agent.register_node(node_id)
    return {"ok": True, "node": node_id}


@router.post("/edge/{src}/{dst}")
def add_edge(src: str, dst: str):
    graph_agent.add_edge(src, dst)
    return {"ok": True, "edge": {"src": src, "dst": dst}}


@router.get("/dump")
def dump_graph():
    return graph_agent.get_graph()


@router.post("/populate")
def populate_graph(
    skills_root: Optional[str] = Query("skills"),
    backend_root: Optional[str] = Query("backend/app"),
    include_imports: Optional[bool] = Query(True),
):
    graph_agent.clear()
    graph_agent.populate_from_skills(skills_root)
    if include_imports:
        graph_agent.populate_from_imports(".", skills_root=skills_root, backend_root=backend_root)
    return {
        "ok": True,
        "nodes": len(graph_agent.nodes),
        "edges": len(graph_agent.edges),
        "skills_root": skills_root,
        "backend_root": backend_root,
        "include_imports": include_imports,
    }


@router.post("/save")
def save_graph(path: Optional[str] = Query(None)):
    p = path or DEFAULT_STORE_PATH
    graph_agent.save(p)
    return {"ok": True, "path": p}


@router.post("/load")
def load_graph(path: Optional[str] = Query(None)):
    p = path or DEFAULT_STORE_PATH
    graph_agent.load(p)
    return {"ok": True, "path": p}


@router.get("/subgraph")
def subgraph(
    node: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    edge_type: Optional[str] = Query(None),
):
    g = graph_agent.get_subgraph(node_id=node, category=category, edge_type=edge_type)
    return g


@router.get("/export/dot")
def export_dot():
    content = graph_agent.to_dot()
    return Response(content=content, media_type="text/plain")


@router.get("/export/mermaid")
def export_mermaid():
    content = graph_agent.to_mermaid()
    return Response(content=content, media_type="text/plain")
