import hashlib   # for the SHA-256 hashes of the input files
import uuid      # for the unique witness ID
import yaml      # PyYAML: pip install pyyaml
from datetime import datetime, timezone


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------

def sha256(path):
    """Hash the input file's raw bytes.

    The witness pins the exact file the verifier saw via
    `input_file_hashes`, so hash the file as given, without
    preprocessing or normalizing line endings.
    """
    with open(path, "rb") as f:          # "rb": hash bytes, not decoded text
        return hashlib.sha256(f.read()).hexdigest()

# ---------------------------------------------------------------
# Layer 2: metadata (provenance: tool, program, specification)
# ---------------------------------------------------------------

def metadata(producer, version, input_files, spec, data_model="ILP32"):
    """Build the `metadata` block that every entry must have.

    NOTE: the exact key names and allowed values are defined in
    format/schemas/common/. Copy them from the schema or from one
    of your linter-passing examples; don't trust this function blindly.
    """
    return {
        # The guide is version 2.3.1-dev, so check which value the
        # schema accepts. "2.0" is a placeholder.
        "format_version": "2.0",
        # Together with the other fields, this uniquely identifies the witness.
        "uuid": str(uuid.uuid4()),
        # ISO 8601 timestamp in UTC, e.g. 2026-10-27T12:00:00+00:00
        "creation_time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "producer": {"name": producer, "version": version},
        "task": {
            # Must be exactly the files given to the verifier.
            "input_files": input_files,
            # Maps each file name to its hash, so a validator can check
            # that the witness belongs to this exact source.
            "input_file_hashes": {f: sha256(f) for f in input_files},
            # The property checked, e.g.
            # "CHECK( init(main()), LTL(G ! call(reach_error())) )"
            "specification": spec,
            "data_model": data_model,   # ILP32 or LP64
            "language": "C",
        },
    }


# ---------------------------------------------------------------
# Entries (top-level list items)
# ---------------------------------------------------------------

def violation_witness(meta, segments):
    """A violation witness is a list with exactly ONE entry.

    The order of `segments` matters: they must be matched in the
    order they are listed.
    """
    return [{
        "entry_type": "violation_sequence",
        "metadata": meta,
        "content": segments,
    }]


def invariant_set(meta, invariants):
    """Correctness witness entry holding invariants.

    Each invariant is a dict with type, location, value and format
    (e.g. loop_invariant). Contracts would go in the same content
    list as {"contract": {...}}.
    """
    return [{
        "entry_type": "invariant_set",
        "metadata": meta,
        "content": [{"invariant": i} for i in invariants],
    }]


def dump(witness, path):
    """Write the witness to a YAML file."""
    with open(path, "w") as f:
        # sort_keys=False keeps the order we built (readable output).
        # default_flow_style=False gives block style instead of {a: b}.
        yaml.safe_dump(witness, f, sort_keys=False, default_flow_style=False)

def generateWitnessYml(filepath, producer=None, version=None, input_files=None, spec=None):

    meta = metadata(producer=producer, version=version, input_files=input_files, spec=spec)
    witness = violation_witness(meta,)
    return dump(witness, filepath)