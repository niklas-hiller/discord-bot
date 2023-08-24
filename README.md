# discord-bot

## Installation after git clone
```powershell
// Check if version is python version is >=3.10
python --version

// Create virtual environment
python -m venv venv

// Activate virtual environment
venv/Scripts/Activate.ps1

// Install all requirements
pip install -r requirements.txt

// Install spacy
```

## Running script
```powershell
// Run main.py
python main.py

// It should display a error that you dont have a config.yml and generates automatically a template
// Put your discord bot token into the config.yml discord.token field

// Run main.py again
python main.py
```

## Music features
This feature requires ffmpeg.exe in the root folder of your application.
You can download ffmpeg on their [official website](https://www.ffmpeg.org/).