import glob
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from c_parser.cParser import analyze_program
from c_parser.visitor import NodeVisitor
from witness_generator.segmentList import SegmentList
from witness_generator.witnessGenerator import *


def clear_output_dir(output_dir: Path):
    """Remove all contents inside the output directory, then recreate it."""
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    output_dir.mkdir(parents=True, exist_ok=True)


def generate_summary(output_dir: Path, c_file: str, segmentlists: list[SegmentList], num_witnesses: int):
    """Write a Markdown summary of the generated witness files."""
    summary_path = output_dir / "summary.md"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = []
    lines.append("# Witness Generation Summary\n")
    lines.append(f"- **Generated at:** {timestamp}\n")
    lines.append(f"- **Input file:** `{c_file}`\n")
    lines.append(f"- **Total witnesses generated:** {num_witnesses}\n")
    lines.append("")
    lines.append("## Generated Files\n")
    lines.append("| # | File Path | Segments | Description |")
    lines.append("|---|-----------|----------|-------------|")

    for i, segmentlist in enumerate(segmentlists):
        seg_count = len(segmentlist.segments)
        filepath = output_dir / f"witness_{i}.yml"
        lines.append(f"| {i} | `{filepath}` | {seg_count} | Violation witness for execution path {i} |")

    summary_rel = output_dir / "summary.md"
    lines.append("")
    lines.append(f"| - | `{summary_rel}` | - | This summary file |")
    lines.append("")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nSummary written to: {summary_path}")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python Start.py <c_file> [output_dir]")
        sys.exit(1)

    c_file = sys.argv[1]
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output")

    # Clear output directory before generating new files
    clear_output_dir(output_dir)
    print(f"Output directory cleared: {output_dir}")

    with open(c_file, "r", encoding="utf-8-sig") as f:
        source = f.read()

    ast = analyze_program(source, filename=c_file)

    segmentlists = []
    visitor = NodeVisitor(segmentlists)
    visitor.visit(ast)

    print(".....................................................")
    visitor.printSegmentList()

    # Generate witness YAML files into the output directory
    for i, segmentlist in enumerate(visitor.segmentlists):
        filepath = output_dir / f"witness_{i}.yml"
        generateWitnessYml(
            str(filepath),
            producer="me",
            version="1.0",
            input_files=[c_file],
            spec="CHECK( init(main()), LTL(G ! call(reach_error())) )",
            segments=segmentlist.to_dict(),
        )
        print(f"Generated: {filepath}")

    # Generate summary Markdown file
    generate_summary(output_dir, c_file, visitor.segmentlists, len(visitor.segmentlists))
    print(f"\nDone. {len(visitor.segmentlists)} witness(es) written to {output_dir}/")
