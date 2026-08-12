"""Constrói GenerationRequest a partir de ResponseSpecification."""

from __future__ import annotations

from typing import Any

from app.language.constants import LengthHint, OutputFormat
from app.language.models.generation import GenerationRequest


class InstructionBuilder:
    """Converte ResponseSpecification (dict ou objeto) em GenerationRequest."""

    def from_spec(self, spec: Any) -> GenerationRequest:
        if hasattr(spec, "to_dict"):
            data = spec.to_dict()
        elif isinstance(spec, dict):
            data = spec
        else:
            data = {
                "key_points": getattr(spec, "key_points", []),
                "tone": getattr(spec, "tone", "neutral"),
                "style_hints": getattr(spec, "style_hints", {}),
                "context_summary": getattr(spec, "context_summary", []),
                "decision_summary": getattr(spec, "decision_summary", ""),
                "intent": getattr(spec, "intent", ""),
                "language": getattr(spec, "language", "pt-BR"),
                "max_length": getattr(spec, "max_length", "medium"),
                "correlation_id": getattr(spec, "correlation_id", None),
                "should_ask_clarification": getattr(spec, "should_ask_clarification", False),
                "clarification_question": getattr(spec, "clarification_question", None),
                "metadata": getattr(spec, "metadata", {}),
            }

        length_raw = data.get("max_length", "medium")
        try:
            length = LengthHint(length_raw)
        except ValueError:
            length = LengthHint.MEDIUM

        instructions = self._build_instructions(data)
        style = {
            "tone": data.get("tone", "neutral"),
            **(data.get("style_hints") or {}),
        }

        return GenerationRequest(
            instructions=instructions,
            style=style,
            context_blocks=list(data.get("context_summary") or []),
            key_points=list(data.get("key_points") or []),
            language=data.get("language", "pt-BR"),
            output_format=OutputFormat.TEXT,
            length=length,
            correlation_id=data.get("correlation_id"),
            metadata={
                "intent": data.get("intent", ""),
                "decision_summary": data.get("decision_summary", ""),
                "should_ask_clarification": data.get("should_ask_clarification", False),
                "clarification_question": data.get("clarification_question"),
                "user_text": (data.get("metadata") or {}).get("user_text", ""),
            },
        )

    def _build_instructions(self, data: dict) -> str:
        parts = [
            "Gere uma resposta natural em português brasileiro.",
            f"Tom: {data.get('tone', 'neutral')}.",
        ]
        if data.get("decision_summary"):
            parts.append(f"Decisão/orientação: {data['decision_summary']}")
        for point in data.get("key_points") or []:
            parts.append(f"- {point}")
        if data.get("should_ask_clarification") and data.get("clarification_question"):
            parts.append(f"Pergunte: {data['clarification_question']}")
        return "\n".join(parts)
