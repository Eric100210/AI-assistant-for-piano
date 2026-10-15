"""Couche HTTP (FastAPI) de MusAIc.

Expose le cœur ``musaic`` (pipeline audio, moteur musical, RAG) sous forme
d'API REST consommée par le front (``frontend/``).

Sous-modules :
    schemas.py  — contrat de données Pydantic (miroir de frontend/src/types.ts)
    services.py — adaptateurs ``musaic`` -> schémas d'API (logique métier)
    routers/    — routes HTTP regroupées par thème
    main.py     — assemblage de l'application (app, CORS, inclusion des routers)
"""
