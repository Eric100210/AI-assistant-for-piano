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
- Get the simultaneous notes to identify potential chords
- Identify the precise chord by comparing to known chords with a score function
- Convert the chord into degrees (conventional notation for music)
- Suggest the next chord by comparing to a dataset of usual chord progressions



MIDI : Musical Instrument Digital Interface. It is structured data containing the note and with what velocity we played it.