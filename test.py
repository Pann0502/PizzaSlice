from importlib.resources import files
from pathlib import Path

from fm_weck import Config
from fm_weck.serve import run_guided

# fm-weck bundles the fm-tools YAML files; point it at the one for your tool
tool_yml = Path(str(files("fm_weck.resources.fm_tools") / "cpachecker.yml"))

config = Config()

# Use a witness-validation version to verify a .yml witness file
# "validation-violation" checks violation witnesses (error traces)
# "validation-correctness" checks correctness witnesses (proofs)
run_guided(
    fm_tool=tool_yml,
    version="4.0-validation-violation",  # validates violation witness files
    configuration=config,
    prop=None,                            # no property file needed for witness validation
    program_files=[Path("src/easycode.c")],  # the original program the witness was generated from
    witness=Path("src/output/witness_0.yml"),  # the witness file to validate
    additional_args=[],
)