.DEFAULT_GOAL := help

PYTHON ?= python

.PHONY: help install install-frontend setup api web test ingest progressions build

help:
	@echo "MusAIc — commandes disponibles :"
	@echo ""
	@echo "  make install           Installe le backend en mode éditable (extra api)"
	@echo "  make install-frontend  Installe les dépendances du frontend"
	@echo "  make setup             Installe le backend et le frontend"
	@echo "  make api               Lance l'API FastAPI sur http://localhost:8000"
	@echo "  make web               Lance le dev server Vite sur http://localhost:5173"
	@echo "  make test              Lance les tests pytest"
	@echo "  make ingest            Reconstruit la base Chroma"
	@echo "  make progressions      Régénère backend/src/musaic/engine/progressions.json"
	@echo "  make build             Build de production du frontend"

install:
	$(PYTHON) -m pip install -e "backend[api]"

install-frontend:
	cd frontend && npm install

setup: install install-frontend

api:
	cd backend && PYTHONPATH=src $(PYTHON) -m uvicorn musaic.api.main:app --reload --port 8000

web:
	cd frontend && npm run dev

test:
	cd backend && $(PYTHON) -m pytest

ingest:
	cd backend && PYTHONPATH=src $(PYTHON) -m musaic.rag.ingestion

progressions:
	cd backend && PYTHONPATH=src $(PYTHON) scripts/build_progressions.py

build:
	cd frontend && npm run build
