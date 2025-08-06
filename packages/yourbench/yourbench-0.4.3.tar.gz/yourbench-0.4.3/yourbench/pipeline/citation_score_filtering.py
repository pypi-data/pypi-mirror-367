"""Compute overlap based citation scores for the lighteval dataset."""

from typing import Sequence
from dataclasses import dataclass

from loguru import logger
from thefuzz import fuzz

from yourbench.utils.dataset_engine import custom_load_dataset, custom_save_dataset, replace_dataset_columns
from yourbench.utils.configuration_engine import YourbenchConfig


@dataclass(slots=True)
class StageConfig:
    run: bool = False
    subset: str = "prepared_lighteval"
    alpha: float = 0.7
    beta: float = 0.3


def _get_stage_config(config: YourbenchConfig) -> StageConfig:
    stage_cfg = config.pipeline_config.citation_score_filtering
    return StageConfig(
        run=stage_cfg.run,
        subset=getattr(stage_cfg, "subset", "prepared_lighteval"),
        alpha=getattr(stage_cfg, "alpha", 0.7),
        beta=getattr(stage_cfg, "beta", 0.3),
    )


@dataclass(slots=True)
class CitationScoreCalculator:
    alpha: float
    beta: float

    def _ratio(self, a: str, b: str) -> int:
        return fuzz.partial_ratio(a, b)

    def compute(self, citations: Sequence[str], chunks: Sequence[str], answer: str) -> tuple[float, float, float]:
        if not citations or (not chunks and not answer):
            return 0.0, 0.0, 0.0

        citation_count = len(citations)
        chunk_scores = [max((self._ratio(c, ch) for ch in chunks), default=0) for c in citations]
        ans_scores = [self._ratio(c, answer) for c in citations]

        avg_chunk = sum(chunk_scores) / citation_count
        avg_ans = sum(ans_scores) / citation_count
        final = self.alpha * avg_chunk + self.beta * avg_ans

        return avg_ans, avg_chunk, final


def run(config: YourbenchConfig) -> None:
    """Entry point for the citation score filtering stage."""
    stage_cfg = _get_stage_config(config)
    if not stage_cfg.run:
        logger.info("citation_score_filtering stage is disabled. Skipping.")
        return

    logger.info(f"Loading '{stage_cfg.subset}' subset for citation score filtering...")
    try:
        lighteval_ds = custom_load_dataset(config=config, subset=stage_cfg.subset)
    except Exception as e:
        logger.exception(f"Could not load subset '{stage_cfg.subset}': {e}")
        return

    if len(lighteval_ds) == 0:
        logger.warning("Dataset is empty; nothing to process.")
        return

    logger.debug(f"Computing citation scores for {len(lighteval_ds)} rows")
    scorer = CitationScoreCalculator(stage_cfg.alpha, stage_cfg.beta)

    all_answer_citation_scores = []
    all_chunk_citation_scores = []
    all_final_scores = []

    for row in lighteval_ds:
        ans_score, chunk_score, final_score = scorer.compute(
            citations=row.get("citations", []),
            chunks=row.get("chunks", []),
            answer=row.get("ground_truth_answer", ""),
        )
        all_answer_citation_scores.append(ans_score)
        all_chunk_citation_scores.append(chunk_score)
        all_final_scores.append(final_score)
    # Use helper function to replace columns cleanly
    # Note: This doesn't preserve original column metadata, but for computed float scores
    # this is acceptable as type inference will correctly identify them as numeric
    columns_data = {
        "answer_citation_score": all_answer_citation_scores,
        "chunk_citation_score": all_chunk_citation_scores,
        "citation_score": all_final_scores,
    }

    lighteval_ds = replace_dataset_columns(lighteval_ds, columns_data)

    logger.info("Saving updated dataset with new citation score columns...")
    custom_save_dataset(dataset=lighteval_ds, config=config, subset=stage_cfg.subset)
    logger.success("citation_score_filtering stage completed successfully.")
