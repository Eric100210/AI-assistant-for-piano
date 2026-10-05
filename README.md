# AI-assistant-for-piano
Design of an AI assistant for piano improvisation and composition, combining a RAG system based on my music theory resources and an audio analysis to recognize played chords and propose suitable chord sequences for improvisation.

In practice, the audio analysis identifies the played chords, a musical engine suggests the next chord, and further explanation or chord variations can be presented thanks to the RAG if the user wishes to delve into the theory.


Problems identified:
- transforming chords in degrees after the audio analysis (we must know the key, not always possible when only playing chords)