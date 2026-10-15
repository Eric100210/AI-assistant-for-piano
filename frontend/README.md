# MusAIc — Front-end

Interface web de **MusAIc**, l'assistant d'improvisation et de composition au piano.

> **État actuel : connecté au back-end FastAPI.** Le parcours complet est
> fonctionnel (upload → analyse → chat). Les appels réseau vivent dans
> `src/api/client.ts` et passent par `/api`, proxyfié par Vite vers
> `http://localhost:8000`.

## Stack

- **React 18** + **TypeScript**
- **Vite** (dev server + build)
- **CSS Modules** pour le style (aucune librairie UI, tout est fait main)
- Aucune dépendance d'exécution au-delà de React

## Démarrer

Le front a besoin de l'API MusAIc (voir le README racine). Dans deux terminaux :

```bash
# 1) back-end, à la racine du dépôt
pip install -e ".[api]"
musaic-api                 # http://localhost:8000

# 2) front-end
cd frontend
npm install
npm run dev                # http://localhost:5173
```

Autres commandes :

```bash
npm run build      # build de production dans dist/
npm run preview    # prévisualiser le build
npm run typecheck  # vérification des types uniquement
```

> `POST /api/chat` a besoin qu'Ollama tourne (`llama3.2:3b`, `nomic-embed-text`)
> et que la base Chroma soit construite (`python -m musaic.rag.ingestion`). Sans
> ça, l'analyse audio fonctionne mais l'assistant répond par un message de repli.

## Parcours utilisateur

1. **Au départ** : seuls le hero et la zone d'import sont affichés.
2. **Au dépôt d'un fichier** : un panneau « Analyse en cours » apparaît, puis les
   panneaux **Analyse** (tonalité, accords, suggestion) et **Assistant MusAIc**
   (chat) se révèlent.
3. **Chat** : posez une question (Entrée pour envoyer). Les réponses viennent du
   RAG local via `POST /api/chat`.

## Structure

```
frontend/
├── index.html
├── vite.config.ts            # build + proxy `/api` -> localhost:8000
├── src/
│   ├── main.tsx              # point d'entrée React
│   ├── App.tsx               # état global + composition de la page
│   ├── types.ts              # types du domaine (miroir de src/musaic/api/schemas.py)
│   ├── api/client.ts         # appels `fetch` à l'API FastAPI
│   ├── styles/globals.css    # design tokens + reset
│   └── components/
│       ├── AppHeader.tsx        # en-tête / marque
│       ├── Panel.tsx            # carte de section réutilisable
│       ├── UploadPanel.tsx      # étape 1 — import audio (drag & drop)
│       ├── AnalyzingPanel.tsx   # état de chargement
│       ├── AnalysisPanel.tsx    # étape 2 — tonalité, accords, suggestion
│       ├── ChatPanel.tsx        # étape 3 — conversation RAG
│       └── Icons.tsx            # icônes SVG
```

## Contrat d'API

Le front consomme deux endpoints, servis par `src/musaic/api/` :

| Fonction (`src/api/client.ts`) | Endpoint | Corps / réponse |
| --- | --- | --- |
| `analyzeAudio(file)` | `POST /api/analyze` | multipart `file` → `Analysis` |
| `sendMessage(query, history)` | `POST /api/chat` | `{ query, history }` → `{ response }` |

Les types de `src/types.ts` décrivent exactement ces réponses (ils sont le miroir
des schémas Pydantic de `src/musaic/api/schemas.py`).

## Design

Thème sombre « studio » : fond profond, halos violet/cyan, typographie
`Space Grotesk` + `Inter`. Les couleurs et rayons sont centralisés dans les
design tokens de `src/styles/globals.css` (`:root { --… }`).
