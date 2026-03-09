#!/bin/bash

ollama serve &
sleep 5
python3 /var/www/html/app.py