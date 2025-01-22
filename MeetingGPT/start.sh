#!/bin/bash
apt-get update && apt-get install -y portaudio19-dev pulseaudio
pip install --no-cache-dir -r requirements.txt
streamlit run meeting_main.py --server.port=$PORT --server.address=0.0.0.0
