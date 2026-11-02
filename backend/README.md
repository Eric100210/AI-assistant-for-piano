# MusAIc — Back-end

Cœur Python de **MusAIc** : analyse audio, moteur musical et RAG, exposés à
l'interface web via une API FastAPI.

## Stack

- **Python ≥ 3.10**, packaging `setuptools` (layout `src/`)
- **FastAPI** + **uvicorn** pour la couche HTTP
- **basic-pitch** / **pychord** pour l'analyse audio et la détection d'accords
- **LangChain** + **Chroma** + **Ollama** pour le RAG

## Démarrer

Depuis la racine du dépôt :

```bash
make install            # pip install -e "backend[api]"
make api                # musaic-api -> http://localhost:8000
```

Ou sans Makefile :

```bash
pip install -e "backend[api]"
musaic-api
```

Documentation interactive de l'API : <http://localhost:8000/docs>.

## Commandes utiles

```bash
make test               # tests (pytest)
make ingest             # reconstruit la base Chroma
make progressions       # régénère backend/src/musaic/engine/progressions.json
```

Équivalents directs :

```bash
cd backend
pytest
python -m musaic.rag.ingestion
python scripts/build_progressions.py
```

## Structure

```text
backend/
├── pyproject.toml          # packaging + dépendances + config pytest
├── src/musaic/             # package Python importable
│   ├── config.py           # source unique des chemins, modèles et paramètres
│   ├── pipeline.py         # audio -> suggestion d'accords
│   ├── cli.py              # point d'entrée `musaic`
│   ├── api/                # application FastAPI (routers, schémas, services)
│   ├── audio/              # transcription + détection d'accords
│   ├── engine/             # tonalité, degrés, suggestions
│   └── rag/                # ingestion, retrieval, chat
├── tests/                  # tests pytest
├── scripts/                # scripts de maintenance
├── data/                   # base de connaissances + audios de test
└── db/                     # base Chroma persistée (générée, non versionnée)
```

`config.py` résout les chemins depuis `backend/` : `data/` et `db/` sont donc
toujours trouvés, quel que soit le répertoire courant. La variable
d'environnement `MUSAIC_ROOT` permet de surcharger cette racine.

## Modèles Ollama requis

```bash
ollama pull llama3.2:3b       # LLM
ollama pull nomic-embed-text  # embeddings
```

`POST /api/chat` a besoin qu'Ollama tourne et que la base Chroma soit construite
(`make ingest`). Sans cela, l'analyse audio fonctionne mais l'assistant répond
par un message de repli.
