"""High-level :class:`PersonalEvoTaste` façade.

This module glues together storage, extractors and the typed memory
model into the single class most users will interact with.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Union

from .exceptions import ConfigurationError
from .extractors import HeuristicExtractor, RuleExtractor, find_similar_rule
from .logging_config import get_logger
from .models import FeedbackEvent, TasteMemory, TasteRule
from .storage import BaseStorage, PathLike, storage_from_path

logger = get_logger("core")


class PersonalEvoTaste:
    """Developer personal-taste memory & self-evolution engine.

    Parameters
    ----------
    memory_path:
        Path to the persisted memory file.  Mutually exclusive with
        ``storage``.  The backend is inferred from the file extension.
    storage:
        A pre-built :class:`BaseStorage` instance.  Use this to inject a
        custom backend (e.g. cloud blob storage).
    extractor:
        Strategy used to convert raw feedback into a rule.  Defaults to
        :class:`HeuristicExtractor` (no external dependencies).
    decay:
        Multiplicative weight decay applied to every existing rule on
        each :meth:`evolve` call (``0`` disables decay).
    """

    DEFAULT_MEMORY_PATH = "personal_taste_memory.yaml"

    def __init__(
        self,
        memory_path: Optional[PathLike] = None,
        *,
        storage: Optional[BaseStorage] = None,
        extractor: Optional[RuleExtractor] = None,
        decay: float = 0.02,
    ) -> None:
        if memory_path is not None and storage is not None:
            raise ConfigurationError("Pass either memory_path or storage, not both")
        if storage is None:
            storage = storage_from_path(memory_path or self.DEFAULT_MEMORY_PATH)

        self._storage: BaseStorage = storage
        self._extractor: RuleExtractor = extractor or HeuristicExtractor()
        if not 0.0 <= decay < 1.0:
            raise ConfigurationError("decay must be in [0, 1)")
        self._decay = decay
        self.memory: TasteMemory = self._storage.load()

    # ------------------------------------------------------------------
    # Public read API
    # ------------------------------------------------------------------
    @property
    def rules(self) -> List[TasteRule]:
        return list(self.memory.taste_rules)

    def top_rules(self, limit: int = 10, project: Optional[str] = None) -> List[TasteRule]:
        return self.memory.top_rules(limit=limit, project=project)

    # ------------------------------------------------------------------
    # Prompt injection
    # ------------------------------------------------------------------
    def inject_taste(
        self,
        base_prompt: str,
        context: str = "",
        *,
        project: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        """Return ``base_prompt`` enriched with the top-ranked rules."""
        rules = self.top_rules(limit=limit, project=project)
        if not rules:
            return f"{base_prompt}\n\n[PersonalEvoTaste] No taste rules yet."

        lines = [
            f"- ({r.weight:.2f}) {r.rule}  — reason: {r.reason or 'n/a'}"
            f"{' — project: ' + r.project if r.project else ''}"
            for r in rules
        ]
        header = f"[PersonalEvoTaste v{len(self.memory.taste_rules)} rules]"
        context_block = f"\n\nProject context: {context}" if context else ""
        return f"{base_prompt}\n\n{header}\n" + "\n".join(lines) + context_block

    # ------------------------------------------------------------------
    # Evolution
    # ------------------------------------------------------------------
    def evolve(
        self,
        agent_output: str,
        user_feedback: str,
        project_name: str = "",
        *,
        tags: Optional[Iterable[str]] = None,
        persist: bool = True,
    ) -> TasteRule:
        """Distill a new rule from feedback, deduplicate, and persist."""
        new_rule = self._extractor.extract(
            agent_output=agent_output,
            user_feedback=user_feedback,
            project=project_name,
            tags=tags,
        )

        self._apply_decay()

        similar = find_similar_rule(new_rule, self.memory.taste_rules)
        if similar is not None:
            similar.reinforce()
            if project_name and project_name not in (similar.project or ""):
                similar.project = project_name or similar.project
            rule_to_record = similar
            logger.info("Reinforced existing rule %s (hits=%d)", similar.id, similar.hits)
        else:
            self.memory.taste_rules.append(new_rule)
            rule_to_record = new_rule
            logger.info("Added new rule %s", new_rule.id)

        self.memory.history.append(
            FeedbackEvent(
                project=project_name,
                agent_output=agent_output,
                user_feedback=user_feedback,
                rule_id=rule_to_record.id,
            )
        )

        if persist:
            self.save()
        return rule_to_record

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def remove_rule(self, rule_id: str, *, persist: bool = True) -> bool:
        removed = self.memory.remove_rule(rule_id)
        if removed and persist:
            self.save()
        return removed

    def reset(self, *, persist: bool = True) -> None:
        self.memory = TasteMemory()
        if persist:
            self.save()

    def save(self) -> None:
        self._storage.save(self.memory)

    def reload(self) -> None:
        self.memory = self._storage.load()

    # ------------------------------------------------------------------
    def _apply_decay(self) -> None:
        if self._decay <= 0:
            return
        factor = 1.0 - self._decay
        for r in self.memory.taste_rules:
            r.weight = max(r.weight * factor, 0.0)

    # ------------------------------------------------------------------
    # Import / export
    # ------------------------------------------------------------------
    def export_dict(self) -> dict:
        return self.memory.model_dump(mode="json")

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "PersonalEvoTaste":
        return cls(memory_path=path)