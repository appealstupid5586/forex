from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any
from pathlib import Path
import ast
import json
import re


@dataclass
class EnterpriseGraphManager:
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    edges: List[Dict[str, str]] = field(default_factory=list)

    def register_node(self, node_id: str, meta: Dict[str, Any] | None = None) -> None:
        self.nodes.setdefault(node_id, {})
        if meta:
            self.nodes[node_id].update(meta)

    def add_edge(self, src: str, dst: str, label: str | None = None) -> None:
        self.edges.append({"src": src, "dst": dst, "label": label or ""})

    def get_graph(self) -> Dict[str, Any]:
        return {"nodes": self.nodes, "edges": self.edges}

    def clear(self) -> None:
        self.nodes.clear()
        self.edges.clear()

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.get_graph(), indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> None:
        p = Path(path)
        if not p.exists():
            return
        data = json.loads(p.read_text(encoding="utf-8"))
        self.nodes = data.get("nodes", {})
        self.edges = data.get("edges", [])

    def populate_from_skills(self, base_path: str | Path) -> None:
        base = Path(base_path)
        if not base.exists() or not base.is_dir():
            return

        for child in sorted(base.iterdir()):
            if not child.is_dir():
                continue
            if not (child / "__init__.py").exists():
                continue
            node_id = child.name
            meta: Dict[str, Any] = {"category": "skill"}
            readme_file = child / "README.md"
            if readme_file.exists():
                text = readme_file.read_text(encoding="utf-8")
                first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
                if first_line:
                    meta["description"] = first_line.lstrip("# ")
            self.register_node(node_id, meta)

    def populate_from_imports(self, base_path: str | Path, skills_root: str = "skills", backend_root: str = "backend/app") -> None:
        base = Path(base_path)
        skills_dir = base / skills_root
        backend_dir = base / backend_root

        def import_to_skill_node(import_path: str) -> str:
            parts = import_path.split(".")
            if len(parts) >= 2 and parts[0] == "skills":
                return ".".join(parts[:2])
            return import_path

        if backend_dir.exists():
            for path in backend_dir.rglob("*.py"):
                try:
                    text = path.read_text(encoding="utf-8")
                except Exception:
                    continue
                module_id = path.relative_to(base).with_suffix("").as_posix().replace("/", ".")
                self.register_node(module_id, {"category": "agent", "source": str(path.relative_to(base))})
                for imported in self._parse_imports(text, module_id):
                    label = self._classify_import(imported, text)
                    if imported.startswith("skills."):
                        skill_node = import_to_skill_node(imported)
                        self.register_node(skill_node, {"category": "skill"})
                        self.add_edge(module_id, skill_node, label=label)
                    elif imported.startswith("app."):
                        self.register_node(imported, {"category": "runtime"})
                        self.add_edge(module_id, imported, label=label)
                for data_node in self._extract_data_dependencies(text, base):
                    self.register_node(data_node, {"category": "data"})
                    self.add_edge(module_id, data_node, label="data")

        if skills_dir.exists():
            for path in skills_dir.rglob("*.py"):
                try:
                    text = path.read_text(encoding="utf-8")
                except Exception:
                    continue
                module_id = path.relative_to(base).with_suffix("").as_posix().replace("/", ".")
                self.register_node(module_id, {"category": "skill", "source": str(path.relative_to(base))})
                for imported in self._parse_imports(text, module_id):
                    label = self._classify_import(imported, text)
                    if imported.startswith("skills."):
                        imported_node = import_to_skill_node(imported)
                        self.register_node(imported_node, {"category": "skill"})
                        self.add_edge(module_id, imported_node, label=label)
                    elif imported.startswith("app."):
                        self.register_node(imported, {"category": "runtime"})
                        self.add_edge(module_id, imported, label=label)
                for data_node in self._extract_data_dependencies(text, base):
                    self.register_node(data_node, {"category": "data"})
                    self.add_edge(module_id, data_node, label="data")

    @staticmethod
    def _parse_imports(source: str, module_id: str | None = None) -> List[str]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        imports: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                if node.level and module_id:
                    base_pkg = module_id.rsplit(".", 1)[0] if "." in module_id else module_id
                    parents = base_pkg.split(".")
                    if node.level > len(parents):
                        resolved = None
                    else:
                        resolved_parts = parents[: len(parents) - node.level + 1]
                        if module:
                            resolved_parts += module.split(".")
                        resolved = ".".join(resolved_parts)
                    if resolved:
                        imports.append(resolved)
                elif module:
                    imports.append(module)
        return imports

    @staticmethod
    def _classify_import(import_path: str, source: str | None = None) -> str:
        if import_path.startswith("skills."):
            return "capability"
        if import_path.startswith("app."):
            return "runtime"
        if source and (".yaml" in source or ".json" in source or ".csv" in source):
            return "data"
        return "depends_on"

    @staticmethod
    def _extract_data_dependencies(source: str, base: Path) -> List[str]:
        nodes: List[str] = []
        pattern = re.compile(r"[\'\"]([^\'\"]+\.(?:yaml|yml|json|csv))[\'\"]")
        for match in pattern.finditer(source):
            path_text = match.group(1)
            if path_text.startswith("data/") or path_text.startswith("./data/") or path_text.startswith("../data/"):
                normalized = Path(path_text).as_posix()
                nodes.append(f"data:{normalized}")
        return nodes

    def get_subgraph(
        self,
        node_id: str | None = None,
        category: str | None = None,
        edge_type: str | None = None,
    ) -> Dict[str, Any]:
        """Return a subgraph filtered by node, category, or edge type.

        - If `node_id` provided: return node and its immediate neighbors.
        - If `category` provided: return nodes whose meta.get('category') == category and edges between them.
        - If `edge_type` provided: filter edges by label.
        - If neither provided: return full graph.
        """
        def edge_match(e: dict[str, str]) -> bool:
            if edge_type and e.get("label") != edge_type:
                return False
            return True

        if node_id:
            nodes: Dict[str, Any] = {}
            edges: List[Dict[str, str]] = []
            if node_id in self.nodes:
                nodes[node_id] = self.nodes[node_id]
            for e in self.edges:
                if (e["src"] == node_id or e["dst"] == node_id) and edge_match(e):
                    edges.append(e)
                    nodes.setdefault(e["src"], self.nodes.get(e["src"], {}))
                    nodes.setdefault(e["dst"], self.nodes.get(e["dst"], {}))
            return {"nodes": nodes, "edges": edges}

        if category:
            nodes = {nid: meta for nid, meta in self.nodes.items() if meta.get("category") == category}
            node_keys = set(nodes.keys())
            edges = [e for e in self.edges if e["src"] in node_keys and e["dst"] in node_keys and edge_match(e)]
            return {"nodes": nodes, "edges": edges}

        edges = [e for e in self.edges if edge_match(e)]
        return {"nodes": self.nodes, "edges": edges}

    def to_dot(self) -> str:
        lines: List[str] = ["digraph EnterpriseGraph {", "  rankdir=LR;"]
        for nid, meta in self.nodes.items():
            label = meta.get("description", nid)
            category = meta.get("category", "node")
            shape = "box"
            if category == "skill":
                shape = "ellipse"
            elif category == "agent":
                shape = "box"
            elif category == "data":
                shape = "cylinder"
            elif category == "runtime":
                shape = "diamond"
            lines.append(f'  "{nid}" [label="{label}", shape={shape}];')
        for edge in self.edges:
            label = edge.get("label", "")
            if label:
                lines.append(f'  "{edge["src"]}" -> "{edge["dst"]}" [label="{label}"];')
            else:
                lines.append(f'  "{edge["src"]}" -> "{edge["dst"]}";')
        lines.append("}")
        return "\n".join(lines)

    def to_mermaid(self) -> str:
        lines: List[str] = ["flowchart LR"]
        for nid, meta in self.nodes.items():
            category = meta.get("category", "node")
            if category == "skill":
                lines.append(f'  {self._mermaid_id(nid)}["{nid}"]')
            elif category == "agent":
                lines.append(f'  {self._mermaid_id(nid)}{{"{nid}"}}')
            elif category == "data":
                lines.append(f'  {self._mermaid_id(nid)}(("{nid}"))')
            elif category == "runtime":
                lines.append(f'  {self._mermaid_id(nid)}(("{nid}"))')
            else:
                lines.append(f'  {self._mermaid_id(nid)}("{nid}")')
        for edge in self.edges:
            src = self._mermaid_id(edge["src"])
            dst = self._mermaid_id(edge["dst"])
            label = edge.get("label", "")
            if label:
                lines.append(f'  {src} -->|"{label}"| {dst}')
            else:
                lines.append(f'  {src} --> {dst}')
        return "\n".join(lines)

    @staticmethod
    def _mermaid_id(node_id: str) -> str:
        return re.sub(r"[^0-9A-Za-z_]+", "_", node_id)
