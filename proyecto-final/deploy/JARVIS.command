#!/bin/zsh
# Doble clic: abre el HUD de JARVIS y activa el modo manos libres («Hey JARVIS»).
open "http://localhost:8765"
cd "$HOME/Proyectos/JARVIS" || exit 1
printf '\033]0;J.A.R.V.I.S. · oído\007'
.venv/bin/python -m jarvis.voice.ears 2>&1 | grep -v -i -E "warn|repo_id|defaulting|weightnorm|super\(\)"
