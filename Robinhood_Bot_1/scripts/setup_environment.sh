#!/bin/bash
python -m venv venv
source venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p data/historical data/outputs logs
cp .env.example .env
echo "Setup complete. Edit .env file with your credentials."