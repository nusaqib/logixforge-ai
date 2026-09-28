"""LogixForge: agentic PLC programming toolkit for Rockwell Studio 5000.

Pipeline:  project spec (JSON + .rll/.st text)  ->  L5X  ->  Studio 5000 import
           L5X  ->  inspect / validate / review   (offline)
           controller  <->  read / write / download (online, guarded)
"""
__version__ = "0.1.0"
