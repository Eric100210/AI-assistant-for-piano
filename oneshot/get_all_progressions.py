import json
import re
import sys
from pathlib import Path

import yaml

# Allow running this script directly (python oneshot/get_all_progressions.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import PROGRESSIONS_DIR, PROGRESSIONS_JSON


def load_progression(file_path):
    content = file_path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", content, re.DOTALL)
    if not match:
        raise ValueError(f"Front matter YAML introuvable dans '{file_path.name}'.")

    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError(
            f"Les métadonnées de '{file_path.name}' doivent être un objet YAML."
        )

    return {
        "filename": file_path.name,
        "metadata": metadata,
    }


def get_all_progressions(directory=PROGRESSIONS_DIR):
    if not directory.exists():
        raise FileNotFoundError(f"Le dossier '{directory}' est introuvable.")

    files = sorted(directory.glob("*.md"))
    if not files:
        raise ValueError(f"Aucune progression Markdown trouvée dans '{directory}'.")

    return [load_progression(file_path) for file_path in files]


def main(output_file=PROGRESSIONS_JSON):
    progressions = get_all_progressions()
    output_file.write_text(
        json.dumps(progressions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(progressions)} progressions récupérées dans '{output_file}'.")


if __name__ == "__main__":
    main()
