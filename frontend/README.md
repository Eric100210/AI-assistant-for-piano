# MusAIc — Front-end

Interface web de **MusAIc**, l'assistant d'improvisation et de composition au piano.

> **État actuel : démo locale.** Le parcours complet est navigable
> (upload → analyse → chat), mais les appels réseau sont **simulés** dans
> `src/api/client.ts`. Il suffit d'y remplacer deux fonctions par de vrais
> `fetch` pour brancher l'API FastAPI (rien d'autre à toucher).

## Stack

- **React 18** + **TypeScript**
- **Vite** (dev server + build)
- **CSS Modules** pour le style (aucune librairie UI, tout est fait main)
- Aucune dépendance d'exécution au-delà de React

## Démarrer

```bash
cd frontend
npm install
npm run dev
```

Le site est servi sur <http://localhost:5173>.

Autres commandes :

```bash
npm run build      # build de production dans dist/
npm run preview    # prévisualiser le build
npm run typecheck  # vérification des types uniquement
```

## Parcours utilisateur

1. **Au départ** : seuls le hero et la zone d'import sont affichés.
2. **Au dépôt d'un fichier** : un panneau « Analyse en cours » apparaît, puis les
   panneaux **Analyse** (tonalité, accords, suggestion) et **Assistant MusAIc**
   (chat) se révèlent.
3. **Chat** : posez une question (Entrée pour envoyer). Les réponses sont
   simulées tant que l'API n'est pas branchée.

## Structure

```
frontend/
├── index.html
├── vite.config.ts            # build + proxy API (à décommenter)
├── src/
│   ├── main.tsx              # point d'entrée React
│   ├── App.tsx               # état global + composition de la page
│   ├── types.ts              # types du domaine (contrat de données)
│   ├── api/client.ts         # ⭐ appels API (actuellement simulés)
│   ├── data/sample.ts        # données factices (à supprimer)
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

## Brancher le back-end FastAPI

Tout se passe dans **`src/api/client.ts`**. Remplace le corps des deux fonctions
par les appels réels (le code `fetch` exact est fourni, en commentaire, juste
au-dessus de chaque `return`) :

- `analyzeAudio(file)` → `POST /api/analyze` (multipart)
- `sendMessage(query, history)` → `POST /api/chat`

Les types de `src/types.ts` décrivent exactement les réponses attendues
(ils correspondent aux schémas Pydantic de `src/musaic/api/schemas.py`).

Enfin, dans `vite.config.ts`, décommente le bloc `server.proxy` pour rediriger
`/api` vers `http://localhost:8000` et éviter tout souci de CORS.

## Design

Thème sombre « studio » : fond profond, halos violet/cyan, typographie
`Space Grotesk` + `Inter`. Les couleurs et rayons sont centralisés dans les
design tokens de `src/styles/globals.css` (`:root { --… }`).
