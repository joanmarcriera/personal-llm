from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from personal_llm.config.settings import AppSettings
from personal_llm.core.io import ensure_directory, read_jsonl, write_jsonl


@dataclass(slots=True)
class MLXTrainingManager:
    settings: AppSettings

    def run(self, config_path: Path, dataset_path: Path | None, dry_run: bool = True) -> list[str]:
        config = self.settings.load_yaml(config_path)
        mlx_config = config.get("mlx", {})
        target_dataset = self.settings.resolve(
            dataset_path or config.get("default_dataset", "data/training/example_sft.jsonl")
        )
        output_dir = self.settings.resolve(config.get("adapter_output_dir", "adapters/output"))
        dataset_dir = self._prepare_dataset_dir(target_dataset)
        generated_config = self._write_generated_config(
            mlx_config=mlx_config,
            dataset_dir=dataset_dir,
            output_dir=output_dir,
        )
        command = ["python", "-m", "mlx_lm", "lora", "--config", str(generated_config)]
        if not dry_run:
            subprocess.run(command, check=True)
        return command

    def _prepare_dataset_dir(self, dataset_path: Path) -> Path:
        dataset_dir = ensure_directory(self.settings.resolve("data/training/generated/mlx"))
        rows = read_jsonl(dataset_path)
        messages_rows = [self._to_chat_record(row) for row in rows]
        if not messages_rows:
            raise ValueError(f"No training examples found in {dataset_path}")
        split_index = max(1, len(messages_rows) // 10)
        valid_rows = messages_rows[:split_index]
        test_rows = messages_rows[:split_index]
        train_rows = messages_rows
        write_jsonl(dataset_dir / "train.jsonl", train_rows)
        write_jsonl(dataset_dir / "valid.jsonl", valid_rows)
        write_jsonl(dataset_dir / "test.jsonl", test_rows)
        return dataset_dir

    @staticmethod
    def _to_chat_record(row: dict[str, Any]) -> dict[str, Any]:
        if "messages" in row and isinstance(row["messages"], list):
            return {"messages": row["messages"]}
        messages = []
        system = row.get("system")
        user = row.get("user")
        assistant = row.get("assistant")
        if isinstance(system, str) and system:
            messages.append({"role": "system", "content": system})
        if isinstance(user, str) and user:
            messages.append({"role": "user", "content": user})
        if isinstance(assistant, str) and assistant:
            messages.append({"role": "assistant", "content": assistant})
        if not messages:
            raise ValueError(
                "Training rows must contain either 'messages' or system/user/assistant fields."
            )
        return {"messages": messages}

    def _write_generated_config(
        self,
        mlx_config: dict[str, Any],
        dataset_dir: Path,
        output_dir: Path,
    ) -> Path:
        generated_config = self.settings.resolve("adapters/generated/mlx-lora-config.yaml")
        ensure_directory(generated_config.parent)
        config_payload = {
            "model": str(mlx_config.get("model", "Qwen/Qwen2.5-7B-Instruct")),
            "train": True,
            "data": str(dataset_dir),
            "fine_tune_type": "lora",
            "num_layers": int(mlx_config.get("num_layers", 16)),
            "batch_size": int(mlx_config.get("batch_size", 2)),
            "iters": int(int(mlx_config.get("num_epochs", 3)) * 100),
            "learning_rate": float(mlx_config.get("learning_rate", 2e-4)),
            "grad_accumulation_steps": int(mlx_config.get("gradient_accumulation_steps", 8)),
            "max_seq_length": int(mlx_config.get("max_seq_length", 4096)),
            "adapter_path": str(output_dir),
            "lora_parameters": {
                "rank": int(mlx_config.get("lora_rank", 16)),
                "dropout": float(mlx_config.get("lora_dropout", 0.05)),
                "scale": float(mlx_config.get("lora_alpha", 32)),
            },
        }
        generated_config.write_text(
            yaml.safe_dump(config_payload, sort_keys=False), encoding="utf-8"
        )
        return generated_config
