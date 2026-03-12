from __future__ import annotations

from pathlib import Path

from personal_llm.config.settings import get_settings
from personal_llm.training.mlx_lora import MLXTrainingManager


def test_mlx_training_manager_generates_dataset_dir_and_config(tmp_path: Path) -> None:
    settings = get_settings().model_copy(update={"home": tmp_path})
    config_dir = tmp_path / "config"
    training_dir = tmp_path / "data" / "training"
    config_dir.mkdir(parents=True)
    training_dir.mkdir(parents=True)

    (config_dir / "training.yaml").write_text(
        Path("config/training.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (training_dir / "example_sft.jsonl").write_text(
        Path("data/training/example_sft.jsonl").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    manager = MLXTrainingManager(settings=settings)
    command = manager.run(
        config_path=Path("config/training.yaml"),
        dataset_path=Path("data/training/example_sft.jsonl"),
        dry_run=True,
    )

    generated_dataset = tmp_path / "data" / "training" / "generated" / "mlx" / "train.jsonl"
    generated_config = tmp_path / "adapters" / "generated" / "mlx-lora-config.yaml"

    assert command[:4] == ["python", "-m", "mlx_lm", "lora"]
    assert generated_dataset.exists()
    assert generated_config.exists()
    assert '"messages"' in generated_dataset.read_text(encoding="utf-8")
    assert "Qwen/Qwen2.5-7B-Instruct" in generated_config.read_text(encoding="utf-8")

