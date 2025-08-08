from abc import ABC, abstractmethod
from typing import Optional

from doteval.models import Evaluation, EvaluationStatus, Record

__all__ = ["Storage", "StorageRegistry", "_registry"]


class Storage(ABC):
    """Abstract storage interface"""

    @abstractmethod
    def create_experiment(self, experiment_name: str) -> None:
        """Create an experiment. Should be idempotent - if experiment exists, do nothing."""
        pass

    @abstractmethod
    def delete_experiment(self, experiment_name: str) -> None:
        pass

    @abstractmethod
    def rename_experiment(self, old_name: str, new_name: str) -> None:
        pass

    @abstractmethod
    def list_experiments(self) -> list[str]:
        pass

    @abstractmethod
    def create_evaluation(self, experiment_name: str, evaluation: Evaluation) -> None:
        pass

    @abstractmethod
    def load_evaluation(
        self, experiment_name: str, evaluation_name: str
    ) -> Evaluation | None:
        pass

    @abstractmethod
    def update_evaluation_status(
        self, experiment_name: str, evaluation_name: str, status: EvaluationStatus
    ) -> None:
        pass

    @abstractmethod
    def completed_items(self, experiment_name: str, evaluation_name: str) -> list[int]:
        pass

    @abstractmethod
    def list_evaluations(self, experiment_name: str) -> list[str]:
        pass

    @abstractmethod
    def add_results(
        self,
        experiment_name: str,
        evaluation_name: str,
        results: list[Record],
    ) -> None:
        pass

    @abstractmethod
    def get_results(self, experiment_name: str, evaluation_name: str) -> list[Record]:
        pass

    @abstractmethod
    def remove_error_result(
        self, experiment_name: str, evaluation_name: str, item_id: int
    ) -> None:
        """Remove an errored result for a specific item that will be retried."""
        pass

    def remove_error_results_batch(
        self, experiment_name: str, evaluation_name: str, item_ids: list[int]
    ) -> None:
        """Remove multiple errored results in a batch.

        Default implementation calls remove_error_result for each item.
        Storage backends should override this for better performance.
        """
        for item_id in item_ids:
            self.remove_error_result(experiment_name, evaluation_name, item_id)


class StorageRegistry:
    """Registry for storage backends."""

    def __init__(self) -> None:
        self._backends: dict[str, type[Storage]] = {}

    def register(self, name: str, storage_class: type[Storage]) -> None:
        """Register a storage backend.

        Args:
            name: The name of the backend (e.g., "json", "sqlite", "redis")
            storage_class: The storage class that implements the Storage interface
        """
        self._backends[name] = storage_class

    def get_backend(self, name: str) -> type[Storage]:
        """Get a storage backend by name.

        Args:
            name: The name of the backend

        Returns:
            The storage class

        Raises:
            ValueError: If the backend is not registered
        """
        if name not in self._backends:
            raise ValueError(f"Unknown storage backend: {name}")
        return self._backends[name]

    def list_backends(self) -> list[str]:
        """List all registered backend names."""
        return list(self._backends.keys())


# Global registry instance
_registry = StorageRegistry()
