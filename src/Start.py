import sys

from c_parser.cParser import analyze_program
from c_parser.visitor import NodeVisitor
from witness_generator.astConverterToSegment import SegmentList
from witness_generator.witnessGenerator import *

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python Start.py <c_file>")
        sys.exit(1)

    c_file = sys.argv[1]

    with open(c_file, "r", encoding="utf-8-sig") as f:
        source = f.read()

    ast = analyze_program(source, filename=c_file)

    segmentlists = []
    visitor = NodeVisitor(segmentlists)
    visitor.visit(ast)

    print(".....................................................")
    visitor.printSegmentList()

    for i, segmentlist in enumerate(visitor.segmentlists):
        generateWitnessYml(
            f"witness_{i}.yml",
            producer="me",
            version="1.0",
            input_files=[c_file],
            spec="CHECK( init(main()), LTL(G ! call(reach_error())) )",
            segments=segmentlist.to_dict(),
        )
