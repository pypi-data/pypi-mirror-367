from collections import Counter
from typing import Counter, Iterable, Optional
import itertools

from pgmap.model.paired_read import PairedRead
from pgmap.model.quality_control_statistics import QualityControlStatistics
from pgmap.alignment import pairwise_aligner, grna_cached_aligner


def get_counts(
    paired_reads: Iterable[PairedRead],
    gRNA_mappings: dict[str, set[str]],
    barcodes: set[str],
    gRNA1_error_tolerance: int = 1,
    gRNA2_error_tolerance: int = 1,
    barcode_error_tolerance: int = 1,
) -> Counter[tuple[str, str, str]]:
    """
    Count paired guides for each sample barcode with tolerance for errors. gRNA1 matchs only through
    perfect alignment. gRNA2 aligns if there is a match of a known (gRNA1, gRNA2) pairing having hamming distance
    within the gRNA2 error tolerance. Finally the barcode aligns if there is a match aligned by edit distance
    within a separate barcode error tolerance.

    Args:
        paired_reads (Iterable[PairedRead]): An iterable producing the candidate reads to be counted. Can be
        generator to minimize memory usage.
        gRNA_mappings (dict[str, set[str]]): The known mappings of each reference library gRNA1 to the set of gRNA2s
        the gRNA1 is paired with.
        barcodes (set[str]): The sample barcode sequences.
        gRNA1_error_tolerance (int): The error tolerance for the hamming distance a gRNA1 candidate can be to the
        reference gRNA1.
        gRNA2_error_tolerance (int): The error tolerance for the hamming distance a gRNA2 candidate can be to the
        reference gRNA2.
        barcode_error_tolerance (int): The error tolerance for the edit distance a barcode candidate can be to the
        reference barcode.

    Returns:
        paired_guide_counts (Counter[tuple[str, str, str]]): The counts of each (gRNA1, gRNA2, barcode) detected
        within the paired reads.
    """
    # TODO should we key with sample id instead of barcode sequence?
    # TODO should alignment algorithm be user configurable?

    paired_guide_counts = Counter()

    gRNA1_cached_aligner = grna_cached_aligner.construct_grna_error_alignment_cache(
        gRNA_mappings.keys(), gRNA1_error_tolerance
    )

    gRNA2_cached_aligner = grna_cached_aligner.construct_grna_error_alignment_cache(
        set(itertools.chain.from_iterable(gRNA_mappings.values())),
        gRNA2_error_tolerance,
    )

    for paired_read in paired_reads:
        paired_read.gRNA1_candidate

        if paired_read.gRNA1_candidate not in gRNA1_cached_aligner:
            continue

        gRNA1, _ = gRNA1_cached_aligner[paired_read.gRNA1_candidate]

        if paired_read.gRNA2_candidate not in gRNA2_cached_aligner:
            continue

        gRNA2, _ = gRNA2_cached_aligner[paired_read.gRNA2_candidate]

        if gRNA2 not in gRNA_mappings[gRNA1]:
            continue

        barcode_score, barcode = max(
            (
                pairwise_aligner.edit_distance_score(
                    paired_read.barcode_candidate, reference
                ),
                reference,
            )
            for reference in barcodes
        )

        if (len(barcode) - barcode_score) > barcode_error_tolerance:
            continue

        # TODO data structure for this?
        paired_guide_counts[(gRNA1, gRNA2, barcode)] += 1

    return paired_guide_counts


def get_counts_and_qc_stats(
    paired_reads: Iterable[PairedRead],
    gRNA_mappings: dict[str, set[str]],
    barcodes: set[str],
    gRNA1_error_tolerance: int = 1,
    gRNA2_error_tolerance: int = 1,
    barcode_error_tolerance: int = 1,
) -> tuple[Counter[tuple[str, str, str]], QualityControlStatistics]:
    """
    Count paired guides for each sample barcode with tolerance for errors. gRNA1 matchs only through
    perfect alignment. gRNA2 aligns if there is a match of a known (gRNA1, gRNA2) pairing having hamming distance
    within the gRNA2 error tolerance. Finally the barcode aligns if there is a match aligned by edit distance
    within a separate barcode error tolerance.

    Additionally, compute quality control statistics for the reads. This function may be less efficient than
    getting counts without quality control statistics due to the need to fully align all parts of a candidate read.

    Args:
        paired_reads (Iterable[PairedRead]): An iterable producing the candidate reads to be counted. Can be
        generator to minimize memory usage.
        gRNA_mappings (dict[str, set[str]]): The known mappings of each reference library gRNA1 to the set of gRNA2s
        the gRNA1 is paired with.
        barcodes (set[str]): The sample barcode sequences.
        gRNA1_error_tolerance (int): The error tolerance for the hamming distance a gRNA1 candidate can be to the
        reference gRNA1.
        gRNA2_error_tolerance (int): The error tolerance for the hamming distance a gRNA2 candidate can be to the
        reference gRNA2.
        barcode_error_tolerance (int): The error tolerance for the edit distance a barcode candidate can be to the
        reference barcode.

    Returns:
        paired_guide_counts (Counter[tuple[str, str, str]]): The counts of each (gRNA1, gRNA2, barcode) detected
        within the paired reads.
        quality_control_statistics (QualityControlStatistics): Quality control statistics for the paired reads.
    """
    paired_guide_counts = Counter()

    total_reads = 0
    discard_count = 0
    gRNA1_mismatch_count = 0
    gRNA2_mismatch_count = 0
    barcode_mismatch_count = 0
    gRNAs_align_count = 0
    estimated_recombination_count = 0

    # https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm
    gRNA1_distance_mean = 0
    gRNA2_distance_mean = 0
    barcode_distance_mean = 0
    gRNA1_distance_sk = 0
    gRNA2_distance_sk = 0
    barcode_distance_sk = 0
    k = 1

    gRNA1_cached_aligner = grna_cached_aligner.construct_grna_error_alignment_cache(
        gRNA_mappings.keys(), gRNA1_error_tolerance
    )

    gRNA2_cached_aligner = grna_cached_aligner.construct_grna_error_alignment_cache(
        set(itertools.chain.from_iterable(gRNA_mappings.values())),
        gRNA2_error_tolerance,
    )

    for paired_read in paired_reads:
        paired_read.gRNA1_candidate

        gRNA1, gRNA2, barcode = None, None, None
        recombination = False

        if paired_read.gRNA1_candidate in gRNA1_cached_aligner:
            gRNA1, gRNA1_distance = gRNA1_cached_aligner[paired_read.gRNA1_candidate]
        else:
            gRNA1_mismatch_count += 1

        if paired_read.gRNA2_candidate in gRNA2_cached_aligner:
            gRNA2, gRNA2_distance = gRNA2_cached_aligner[paired_read.gRNA2_candidate]
        else:
            gRNA2_mismatch_count += 1

        if gRNA1 and gRNA2:
            gRNAs_align_count += 1

            if gRNA2 not in gRNA_mappings[gRNA1]:
                recombination = True
                estimated_recombination_count += 1

        barcode_score, barcode = max(
            (
                pairwise_aligner.edit_distance_score(
                    paired_read.barcode_candidate, reference
                ),
                reference,
            )
            for reference in barcodes
        )

        barcode_distance = len(barcode) - barcode_score

        if barcode_distance > barcode_error_tolerance:
            barcode_mismatch_count += 1
            barcode = None

        if gRNA1 and gRNA2 and barcode and not recombination:
            paired_guide_counts[(gRNA1, gRNA2, barcode)] += 1

            gRNA1_distance_mean, gRNA1_distance_sk = _welford_step(
                k, gRNA1_distance, gRNA1_distance_mean, gRNA1_distance_sk
            )

            gRNA2_distance_mean, gRNA2_distance_sk = _welford_step(
                k, gRNA2_distance, gRNA2_distance_mean, gRNA2_distance_sk
            )

            barcode_distance_mean, barcode_distance_sk = _welford_step(
                k, barcode_distance, barcode_distance_mean, barcode_distance_sk
            )

            k += 1
        else:
            discard_count += 1

        total_reads += 1

    if total_reads == 0:
        raise ValueError("Cannot compute QC statistics for reads with length 0.")

    qc_stats = QualityControlStatistics(
        total_reads=total_reads,
        discard_rate=discard_count / total_reads,
        gRNA1_mismatch_rate=gRNA1_mismatch_count / total_reads,
        gRNA2_mismatch_rate=gRNA2_mismatch_count / total_reads,
        barcode_mismatch_rate=barcode_mismatch_count / total_reads,
        estimated_recombination_rate=estimated_recombination_count / gRNAs_align_count,
        gRNA1_distance_mean=gRNA1_distance_mean,
        gRNA2_distance_mean=gRNA2_distance_mean,
        barcode_distance_mean=barcode_distance_mean,
        gRNA1_distance_variance=gRNA1_distance_sk / (k - 1) if k > 1 else 0,
        gRNA2_distance_variance=gRNA2_distance_sk / (k - 1) if k > 1 else 0,
        barcode_distance_variance=barcode_distance_sk / (k - 1) if k > 1 else 0,
    )

    return paired_guide_counts, qc_stats


def _welford_step(
    k: int, xk: float, current_mean: Optional[float], current_sk: Optional[float]
):
    if k == 1:
        return xk, 0

    new_mean = current_mean + (xk - current_mean) / k
    new_sk = current_sk + (xk - current_mean) * (xk - new_mean)

    return new_mean, new_sk
