from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SkillIO:
    name: str
    description: str
    data_type: Optional[str] = None
    required: bool = True
    example: Any = None


@dataclass
class SkillMetadata:
    name: str
    description: str
    version: str = "1.0.0"
    category: Optional[str] = None
    inputs: List[SkillIO] = field(default_factory=list)
    outputs: List[SkillIO] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "inputs": [self._io_to_dict(item) for item in self.inputs],
            "outputs": [self._io_to_dict(item) for item in self.outputs],
            "dependencies": [self._normalize_dependency(item) for item in self.dependencies],
            "examples": [self._normalize_example(item) for item in self.examples],
            "tags": list(self.tags),
        }

    @staticmethod
    def _normalize_dependency(value: Any) -> str:
        return str(value).strip()

    @staticmethod
    def _normalize_example(value: Any) -> Any:
        if isinstance(value, dict):
            normalized = {
                "input": value.get("input"),
                "output": value.get("output"),
            }
            if "notes" in value:
                normalized["notes"] = value.get("notes")
            return normalized
        return value

    @staticmethod
    def _io_to_dict(item: SkillIO) -> Dict[str, Any]:
        return {
            "name": item.name,
            "description": item.description,
            "data_type": item.data_type,
            "required": item.required,
            "example": item.example,
        }
