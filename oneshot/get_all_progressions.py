import json
import re
from pathlib import Path

import yaml


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
PROJECT_DIRECTORY = SCRIPT_DIRECTORY.parent
PROGRESSIONS_DIRECTORY = PROJECT_DIRECTORY / "RAG_knowledge" / "progressions"
MUSICAL_ENGINE = PROJECT_DIRECTORY / "musical_engine"
OUTPUT_FILE = MUSICAL_ENGINE / "progressions.json"


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


def get_all_progressions(directory=PROGRESSIONS_DIRECTORY):
    if not directory.exists():
        raise FileNotFoundError(f"Le dossier '{directory}' est introuvable.")

    files = sorted(directory.glob("*.md"))
    if not files:
        raise ValueError(f"Aucune progression Markdown trouvée dans '{directory}'.")

    return [load_progression(file_path) for file_path in files]


def main(output_file=OUTPUT_FILE):
    progressions = get_all_progressions()
    output_file.write_text(
        json.dumps(progressions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(progressions)} progressions récupérées dans '{output_file}'.")


if __name__ == "__main__":
    main()
