"""Core text processing domain logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence


DEFAULT_PROCESSING_STEPS: tuple[str, ...] = (
    "Tokenizing text",
    "Analyzing semantics",
    "Running classification",
    "Generating response",
    "Finalizing results",
)


def validate_text_input(text: str) -> str:
    """Ensure that text input is non-empty before submitting a task."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    return text


def compute_progress(step: int, total: int) -> int:
    """Compute the integer percentage for a given step."""
    if total <= 0:
        return 0
    return int(100 * step / total)


@dataclass(frozen=True)
class ProcessingStep:
    """Immutable representation of a single processing step."""

    index: int
    description: str
    total_steps: int

    @property
    def progress(self) -> int:
        return compute_progress(self.index, self.total_steps)


class TextProcessor:
    """Domain component responsible for chunk processing semantics."""

    def __init__(self, steps: Sequence[str] | None = None) -> None:
        self._steps: tuple[str, ...] = tuple(steps or DEFAULT_PROCESSING_STEPS)

    def processing_plan(self) -> Iterable[ProcessingStep]:
        """Iterate over configured processing steps."""
        total_steps = len(self._steps)
        for index, description in enumerate(self._steps, start=1):
            yield ProcessingStep(index=index, description=description, total_steps=total_steps)

    @staticmethod
    def process_text_chunk(text: str, step: ProcessingStep) -> str:
        """Produce a textual representation for a processed chunk."""
        preview = text[:20].replace("\n", " ")
        return f"Step {step.index}: {step.description} - '{preview}...'"


def iterate_processing_chunks(text: str, processor: TextProcessor | None = None) -> Iterator[tuple[ProcessingStep, str]]:
    """Yield text processing chunks along with their step metadata."""
    processor = processor or TextProcessor()
    for step in processor.processing_plan():
        yield step, processor.process_text_chunk(text, step)
