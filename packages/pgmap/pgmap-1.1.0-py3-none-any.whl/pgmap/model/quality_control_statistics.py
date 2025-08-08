import typing


class QualityControlStatistics(typing.NamedTuple):
    """
    A summary of quality control statistics for candidate reads.

    Attributes:
        total_reads (int): The total amount of reads regardless of content.
        discard_rate (float): The total rate from 0 to 1 of any kind of discarding of reads.
        gRNA1_mismatch_rate (float): The rate at which gRNA1 candidates do not match a library gRNA1
        allowing error tolerances.
        gRNA2_mismatch_rate (float): The rate at which gRNA2 candidates do not match a library gRNA2
        allowing error tolerances.
        barcode_mismatch_rate (float): The rate at which barcode candidates do not match a library barcode
        allowing error tolerances.
        estimated_recombination_rate (float): The rate at which gRNA1 and gRNA2 candidates are aligned, but the
        combination of gRNA1 and gRNA2 is not a valid pairing from the library.
        gRNA1_distance_mean (float): The mean distance that accepted gRNA1 candidates vary from the closest
        library gRNA1.
        gRNA2_distance_mean (float): The mean distance that accepted gRNA1 candidates vary from the closest
        library gRNA2.
        barcode_distance_mean (float): The mean distance that accepted barcode candidates vary from the closest
        reference barcode.
        gRNA1_distance_variance (float): The variance of the distances that accepted gRNA1 candidates vary
        from the closest library gRNA1.
        gRNA2_distance_variance (float): The variances of the distances that accepted gRNA2 candidates vary
        from the closest library gRNA2.
        barcode_distance_variance (float): The variances of the distances that accepted barcode candidates vary
        from the closest reference barcode.
    """

    total_reads: int
    discard_rate: float
    gRNA1_mismatch_rate: float
    gRNA2_mismatch_rate: float
    barcode_mismatch_rate: float
    estimated_recombination_rate: float
    gRNA1_distance_mean: float
    gRNA2_distance_mean: float
    barcode_distance_mean: float
    gRNA1_distance_variance: float
    gRNA2_distance_variance: float
    barcode_distance_variance: float
