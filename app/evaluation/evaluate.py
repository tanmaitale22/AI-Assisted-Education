from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


class Evaluator:
    """Compute standard classification metrics for the memory-scoring dataset."""

    def __init__(self, dataset_path: str) -> None:
        self._dataset_path = Path(dataset_path)

    def run(self) -> dict[str, Any]:
        with self._dataset_path.open("r", encoding="utf-8") as handle:
            dataset = json.load(handle)

        y_true = [item["label"] for item in dataset]
        y_pred = [item["predicted"] for item in dataset]

        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average="macro", zero_division=0),
            "recall": recall_score(y_true, y_pred, average="macro", zero_division=0),
            "f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
            "confusion_matrix": confusion_matrix(y_true, y_pred, labels=["PERMANENT", "TEMPORARY", "DISCARD"]).tolist(),
        }


if __name__ == "__main__":
    evaluator = Evaluator("app/evaluation/dataset.json")
    print(evaluator.run())
