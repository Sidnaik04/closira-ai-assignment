from pathlib import Path


def load_sop():

    sop_path = Path("app/data/sop.txt")

    return sop_path.read_text(encoding="utf-8")
