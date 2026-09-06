from __future__ import annotations

from dataclasses import dataclass

from personal_llm.core.io import write_jsonl
from personal_llm.core.schemas import ChunkRecord, TrainingExample
from personal_llm.prompts.loader import PromptLibrary


@dataclass(slots=True)
class DatasetBuilder:
    prompts: PromptLibrary

    def build_training_examples(self, chunks: list[ChunkRecord]) -> list[TrainingExample]:
        examples: list[TrainingExample] = []
        system_prompt = self.prompts.system_prompt()
        refusal_prompt = self.prompts.refusal_prompt()
        for chunk in chunks:
            if chunk.classification_label == "disallowed":
                continue
            domains = ", ".join(chunk.domains) or "professional operations"
            user_prompt = (
                f"Use the following professional context to answer a question about {domains}."
            )
            assistant_prompt = (
                f"{chunk.text}\n\nRespond with a concise, evidence-aware explanation "
                "and cite the source context."
            )
            examples.append(
                TrainingExample(
                    id=f"sft::{chunk.id}",
                    system=system_prompt,
                    user=user_prompt,
                    assistant=assistant_prompt,
                    allowed_domains=chunk.domains,
                    source_chunk_ids=[chunk.id],
                )
            )
        if self.prompts.include_refusal_examples():
            refusal_examples = [
                TrainingExample(
                    id="refusal::sports",
                    system=system_prompt,
                    user="Who will win the football league this year?",
                    assistant=refusal_prompt,
                    refusal=True,
                    allowed_domains=[],
                    source_chunk_ids=[],
                    metadata={"policy": "disallowed_topic"},
                ),
                TrainingExample(
                    id="refusal::movies",
                    system=system_prompt,
                    user="Recommend some blockbuster movies for tonight.",
                    assistant=refusal_prompt,
                    refusal=True,
                    allowed_domains=[],
                    source_chunk_ids=[],
                    metadata={"policy": "disallowed_topic"},
                ),
            ]
            examples.extend(refusal_examples)
        return examples

    def write_training_set(self, chunks: list[ChunkRecord], path: str) -> list[TrainingExample]:
        examples = self.build_training_examples(chunks)
        write_jsonl(self.prompts.settings.resolve(path), examples)
        return examples
