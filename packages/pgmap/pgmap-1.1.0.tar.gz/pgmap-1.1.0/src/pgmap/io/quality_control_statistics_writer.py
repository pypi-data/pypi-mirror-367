import argparse
import json
from importlib.metadata import version

from pgmap.model.quality_control_statistics import QualityControlStatistics


def write_quality_control_statistics(
    cli_args: argparse.Namespace, qc_stats: QualityControlStatistics
):
    with open(cli_args.quality_control, "w") as f:
        qc_report = {"input": vars(cli_args), "version": version("pgmap")}
        qc_report.update(qc_stats._asdict())

        json.dump(qc_report, f, indent=4)
