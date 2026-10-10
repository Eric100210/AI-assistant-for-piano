# AI-assistant-for-piano
Design of an AI assistant for piano improvisation and composition, combining a RAG system based on my music theory resources and an audio analysis to recognize played chords and propose suitable chord sequences for improvisation.

In practice, the audio analysis identifies the played chords, a musical engine suggests the next chord, and further explanation or chord variations can be presented thanks to the RAG if the user wishes to delve into the theory.


Problems identified:
- transforming chords in degrees after the audio analysis (we must know the key, not always possible when only playing chords)
- how to properly differentiate the chord with the melody, especially when the chord is played at the same time at the first note of the melody ?


First version of the RAG : 
- Ingestion of my personal musical theory courses (embedding, vector database)
- Conversational RAG with chat history (model OllamaLLM)

First version of audio analysis pipeline:
- Download a .mp3 file
- Transcribe in MIDI Data thanks to basic pitch model
- Get the key and the mode, with Krumhansl-Schmuckler key-finding algorithm
- Get the notes by time with a time window system to identify important notes (notes potentially linked to chords)
- Identify the precise chord for each time with pychord (I tried with a personal chord finder, but less efficient)
- Merge the consecutive chords to get the real chord prediction
- Convert the chords into degrees (conventional notation for music)
Then two options : 
(1): simplify the progression by removing specifications and suggesting the next degree with a deterministic engine (comparing to a dataset). The RAG in this case is used to explain the theory or suggest variations.
(2) : pass the simplify progression and the real one to the RAG, which suggests directly the next one and variations knowing the full real progression



MIDI : Musical Instrument Digital Interface. It is structured data containing the note and with what velocity we played it.