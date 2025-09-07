# Summarization helpers powered by LlamaIndex LLMs.
# Accepts a flexible transcript structure, prepares a prompt, and asks an LLM
# for either plain text or a structured note depending on the requested format.
from __future__ import annotations

import os
from enum import Enum
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field
from django.conf import settings

# LlamaIndex LLMs (OpenAI or Ollama)
from llama_index.core.llms.llm import LLM
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate


def _get_llm() -> LLM:
    """Return an LLM instance based on environment settings.

    - If USE_LOCAL_MODELS is true, use an Ollama endpoint.
    - Otherwise, default to OpenAI-compatible LLM.
    """
    if settings.USE_LOCAL_MODELS:
        return Ollama(
            model=settings.LLM_MODEL,
            request_timeout=360.0,
            base_url=str(settings.OLLAMA_URL) if settings.OLLAMA_URL else None,
        )
    return OpenAI(
        model=settings.LLM_MODEL,
        request_timeout=360.0,
        api_key=settings.OPENAI_API_KEY,
    )


class NoteFormat(str, Enum):
    TEXT = "Text"
    SOAP = "SOAP"
    PKI_HL7_CDA = "PKI HL7 CDA"
    THERAPY_ASSESSMENT = "Therapy Assessment"


class SOAPNote(BaseModel):
    subjective: Optional[str] = Field(description="Patient-reported info")
    objective: Optional[str] = Field(description="Observed findings")
    assessment: Optional[str] = Field(description="Clinical assessment")
    plan: Optional[str] = Field(description="Proposed plan")


class PKIHL7CDANote(BaseModel):
    context_of_visit: Optional[dict] = None
    subjective_history: Optional[dict] = None
    physical_examination: Optional[dict] = None
    diagnoses_and_problems: Optional[dict] = None
    ordered_diagnostics: Optional[dict] = None
    treatment_and_recommendations: Optional[dict] = None
    follow_up_and_observation_plan: Optional[dict] = None
    visit_summary: Optional[dict] = None


class TherapyAssessmentNote(BaseModel):
    alliance: Optional[int] = Field(None, ge=1, le=5)
    communication: Optional[int] = Field(None, ge=1, le=5)
    ethics: Optional[int] = Field(None, ge=1, le=5)
    effectiveness: Optional[int] = Field(None, ge=1, le=5)
    strengths: Optional[str] = None
    improvements: Optional[str] = None


PROMPT = PromptTemplate(
    """
Create a concise clinical note from the transcript below. If a target language is
provided, respond in that language; otherwise, use the transcript's language.
Use only information explicitly present in the transcript. Do NOT invent details.
For structured outputs, return empty strings for missing fields.

---
Target Language: {target_language}
---

Transcript:
{transcript}
"""
)


class SummarizationService:
    def __init__(self) -> None:
        self.llm = _get_llm()

    def _to_text(self, transcript: Any) -> str:
        """Normalize various transcript shapes into plain text.

        Accepted shapes:
        - {"text": "...", "language": "en"}
        - {"segments": [{"text": "..."}, ...], "language": "en"}
        - {"segments": [...], "word_segments": [...], "language": "en"}
        """
        if isinstance(transcript, dict):
            if "text" in transcript and isinstance(transcript["text"], str):
                return transcript["text"]
            if "segments" in transcript and isinstance(transcript["segments"], list):
                return " ".join(str(seg.get("text", "")) for seg in transcript["segments"]).strip()
        return str(transcript)

    def _nullify_empty_strings(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: self._nullify_empty_strings(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._nullify_empty_strings(v) for v in data]
        if isinstance(data, str) and data == "":
            return None
        return data

    def summarize(self, transcript: Any, fmt: NoteFormat, language: Optional[str] = None) -> Any:
        text = self._to_text(transcript)
        prompt = PROMPT.format(transcript=text, target_language=language)

        structured: Dict[NoteFormat, Type[BaseModel]] = {
            NoteFormat.SOAP: SOAPNote,
            NoteFormat.PKI_HL7_CDA: PKIHL7CDANote,
            NoteFormat.THERAPY_ASSESSMENT: TherapyAssessmentNote,
        }

        if fmt in structured:
            try:
                sllm = self.llm.as_structured_llm(structured[fmt])
                resp = sllm.complete(prompt)
            except Exception:
                return {
                    "detail": (
                        "Selected model cannot produce the requested structured format. "
                        "Try a different format or a stronger model."
                    )
                }
            if resp and getattr(resp, "raw", None):
                payload = structured[fmt].model_validate(resp.raw).model_dump()
                return self._nullify_empty_strings(payload)
            return None

        resp = self.llm.complete(prompt)
        return resp.text if resp else None
