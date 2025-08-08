import statistics
from abc import ABC, abstractmethod

from typing import Any, Callable, Awaitable, cast
from dataclasses import dataclass, field
from adaptive_harmony import StringThread
from adaptive_harmony.graders.utils import SuccessJudgeLog, FailedJudgeLog
from adaptive_harmony.logging_table import Table


@dataclass
class ScoreWithMetadata:
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class Grader(ABC):
    """
    Base Grader to inherit from when building a scoring function.
    """

    def __init__(self, logging_name: str | None = None):
        self._logs: list[dict[str, Any]] = []
        self.logging_name = logging_name

    @abstractmethod
    async def score(self, sample: StringThread) -> ScoreWithMetadata:
        """
        Grade a single sample.
        Returns a single float score, with optional metadata.
        Metadata can be useful for evals when LLM reasoning regarding the score is available.
        """
        pass

    async def score_without_metadata(self, sample: StringThread) -> float:
        """Returns only the float score from .score"""
        return (await self.score(sample)).score

    def add_log(self, log_data: dict[str, Any]) -> None:
        """Add a log entry to the scorer's log collection."""
        self._logs.append(log_data)

    def get_logs(self, clear: bool = False, log_all_samples: bool = False) -> dict[str, float | Table]:
        """
        Get aggregated logs from all score calls.
        Base implementation computes statistics for "score" keys in individual logs.
        If there are none, returns empty dict.
        """
        if not self._logs:
            return {}

        scores = [s for s in [log.get("score") for log in self._logs] if s is not None]
        logs = {}
        if scores:
            logs.update(
                dict(
                    **{
                        f"score/{key}": value
                        for key, value in dict(
                            mean=statistics.mean(scores),
                            std=statistics.stdev(scores) if len(scores) > 1 else 0.0,
                            min=min(scores),
                            max=max(scores),
                            count=len(scores),
                        ).items()
                    },
                )
            )
        if clear:
            self.clear_logs()
        return logs

    def clear_logs(self) -> None:
        """
        Clear all accumulated logs.
        """
        self._logs.clear()

    def get_sample_tables(
        self, successful_samples: list[SuccessJudgeLog], failed_samples: list[FailedJudgeLog] | None = None
    ):
        table_logs = {}
        scored_samples = (
            Table()
            .add_column("Prompt", [log["prompt"] for log in successful_samples])
            .add_column("Reasoning", [log.get("reasoning") for log in successful_samples])
            .add_column("Score", [float(log["score"]) for log in successful_samples])
        )
        if failed_samples:

            unscored_samples = (
                Table()
                .add_column("Prompt", [log.get("prompt") for log in failed_samples])
                .add_column("Error", [str(log["error"]) for log in failed_samples])
            )
            table_logs["score/unscored_samples"] = unscored_samples
            table_logs["score/unscored_samples_count"] = len(failed_samples)

        table_logs["score/scored_samples"] = scored_samples
        table_logs["score/scored_samples_count"] = len(successful_samples)
        return table_logs

    @classmethod
    def from_function(cls, async_fn: Callable[[StringThread], Awaitable[float]]) -> "Grader":
        class FunctionScorer(cls):
            def __init__(self):
                super().__init__()

            async def score(self, sample: StringThread) -> ScoreWithMetadata:
                result = await async_fn(sample)
                score_with_metadata = ScoreWithMetadata(score=result, metadata={})
                self.add_log({"score": result})
                return score_with_metadata

        return FunctionScorer()
