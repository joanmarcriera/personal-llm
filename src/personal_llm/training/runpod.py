from __future__ import annotations

import json
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from personal_llm.config.settings import AppSettings


@dataclass(slots=True)
class RunPodTrainingManager:
    settings: AppSettings

    def run(
        self, config_path: Path, dataset_path: Path | None, submit: bool = False
    ) -> dict[str, Any]:
        config = self.settings.load_yaml(config_path)
        remote = config.get("remote", {})
        dataset = self.settings.resolve(
            dataset_path or config.get("default_dataset", "data/training/example_sft.jsonl")
        )
        bundle = self.package_job(dataset, config_path)
        spec = self.build_job_spec(bundle, remote)
        result = {"bundle": str(bundle), "job_spec": spec}
        if submit:
            result["submission"] = self.submit_job(spec)
        return result

    def package_job(self, dataset_path: Path, config_path: Path) -> Path:
        bundle_path = self.settings.resolve(Path("data/training/runpod-job.tar.gz"))
        with tarfile.open(bundle_path, "w:gz") as archive:
            archive.add(dataset_path, arcname="dataset.jsonl")
            archive.add(self.settings.resolve(config_path), arcname="training.yaml")
            archive.add(
                self.settings.resolve(Path("scripts/runpod_entrypoint.sh")),
                arcname="runpod_entrypoint.sh",
            )
        return bundle_path

    def build_job_spec(self, bundle_path: Path, remote_config: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": "personal-llm-lora",
            "imageName": remote_config.get("container_image", "axolotlai/axolotl:main-latest"),
            "gpuType": remote_config.get("gpu_recommendations", {}).get(
                "seven_b", "L4 or A10G 24 GB class"
            ),
            "upload_bundle": str(bundle_path),
            "workspace_dir": remote_config.get("upload_dir", "/workspace/personal-llm-job"),
            "output_dir": remote_config.get("output_dir", "/workspace/output"),
            "entrypoint": "/workspace/personal-llm-job/runpod_entrypoint.sh",
        }

    def submit_job(self, spec: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.runpod_api_key or not self.settings.runpod_template_id:
            raise RuntimeError("RunPod credentials are not configured.")
        client = httpx.Client(
            base_url="https://api.runpod.io/graphql",
            headers={"Authorization": self.settings.runpod_api_key},
            timeout=60.0,
        )
        payload = {
            "query": """
                mutation CreatePod($input: PodFindAndDeployOnDemandInput!) {
                  podFindAndDeployOnDemand(input: $input) {
                    id
                    imageName
                    desiredStatus
                  }
                }
            """,
            "variables": {
                "input": {
                    "templateId": self.settings.runpod_template_id,
                    "dockerArgs": json.dumps(spec),
                }
            },
        }
        response = client.post("", json=payload)
        response.raise_for_status()
        return response.json()
