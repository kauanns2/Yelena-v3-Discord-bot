"""Constrói GenerationRequest a partir de ResponseSpecification."""

from __future__ import annotations

from typing import Any

from app.language.constants import LengthHint, OutputFormat
from app.language.models.generation import GenerationRequest


class InstructionBuilder:
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
                "metadata": getattr(spec, "metadata", {}) or {},
            }

        length_raw = data.get("max_length", "medium")
        try:
            length = LengthHint(length_raw)
        except ValueError:
            length = LengthHint.MEDIUM

        meta_in = dict(data.get("metadata") or {})
        instructions = self._build_instructions(data)
        style = {
            "tone": data.get("tone", "neutral"),
            **(data.get("style_hints") or {}),
        }

        # metadata completo para o LLM (teia)
        meta_out = {
            **meta_in,
            "intent": data.get("intent", ""),
            "decision_summary": data.get("decision_summary", ""),
            "should_ask_clarification": data.get("should_ask_clarification", False),
            "clarification_question": data.get("clarification_question"),
            "user_text": meta_in.get("user_text") or "",
            "identity_brief": meta_in.get("identity_brief") or "",
            "emotion_summary": meta_in.get("emotion_summary") or {},
            "personality_summary": meta_in.get("personality_summary") or {},
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
            metadata=meta_out,
        )

    def _build_instructions(self, data: dict) -> str:
        parts = [
            "Responda como Yelena, em português brasileiro natural.",
            f"Tom: {data.get('tone', 'neutral')}.",
        ]
        if data.get("decision_summary"):
            parts.append(f"Orientação de raciocínio: {data['decision_summary']}")
        for point in data.get("key_points") or []:
            parts.append(f"- {point}")
        return "\n".join(parts)
