# MusAIc — Front-end

Interface web de **MusAIc**, l'assistant d'improvisation et de composition au piano.

> ⚠️ **État actuel : aperçu statique.** L'interface est complète mais **aucune
> interaction n'est branchée** : les données affichées viennent de
> `src/data/sample.ts`. C'est volontaire — le back-end FastAPI sera câblé ensuite.

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

## Structure

```
frontend/
├── index.html
├── vite.config.ts            # build + proxy API (à décommenter)
├── src/
│   ├── main.tsx              # point d'entrée React
│   ├── App.tsx               # composition de la page
│   ├── types.ts              # types du domaine (contrat de données)
│   ├── data/sample.ts        # données factices (à supprimer)
│   ├── styles/globals.css    # design tokens + reset
│   └── components/
│       ├── AppHeader.tsx     # en-tête / marque
│       ├── Panel.tsx         # carte de section réutilisable
│       ├── UploadPanel.tsx   # étape 1 — import audio
│       ├── AnalysisPanel.tsx # étape 2 — tonalité, accords, suggestion
│       ├── ChatPanel.tsx     # étape 3 — conversation RAG
│       └── Icons.tsx         # icônes SVG
```

## Brancher le back-end FastAPI

Le front est prêt à recevoir des données ; il faut seulement les fournir.

1. **Types = contrat.** Les interfaces de `src/types.ts` décrivent exactement ce
   que l'API doit renvoyer :
   - `Analysis` → réponse de `POST /analyze`
   - `ChatMessage` → messages de la conversation

2. **Étape 1 — import audio.** Dans `UploadPanel.tsx`, remplacer la zone
   décorative par un `<input type="file">` (ou un vrai drag & drop) puis un :

   ```ts
   const form = new FormData();
   form.append("file", file);
   const res = await fetch("/api/analyze", { method: "POST", body: form });
   const analysis: Analysis = await res.json();
   ```

3. **Étape 2 — analyse.** Remonter l'`Analysis` dans `App.tsx` (état local) et la
   passer à `<AnalysisPanel analysis={...} />`. Le composant est déjà pilote par
   ses props.

4. **Étape 3 — chat.** Dans `ChatPanel.tsx`, activer le `<textarea>` et envoyer
   `POST /chat`. Pour l'effet « réponse qui s'écrit », utilise un flux SSE
   (`EventSource` ou `fetch` + `ReadableStream`).

5. **CORS / proxy.** En développement, décommenter le bloc `server.proxy` dans
   `vite.config.ts` pour rediriger `/api` vers `http://localhost:8000` et éviter
   les soucis de CORS.

## Design

Thème sombre « studio » : fond profond, halos violet/cyan, typographie
`Space Grotesk` + `Inter`. Les couleurs et rayons sont centralisés dans les
design tokens de `src/styles/globals.css` (`:root { --… }`).
