# Crypto News Agent

This project fetches the top 5 crypto news headlines daily at 7 AM.  
If there is no crypto news, it fetches top stock market news instead.  

## Setup

1. Clone/download the project.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Add your API keys in `config/config.py`:
- `OPENAI_API_KEY` for OpenAI
- `NEWS_API_KEY` for NewsAPI
4. Run the agent locally:
```bash
python main.py
```

## Hosting Options

- **Locally**: Run continuously using `python main.py` or as a background process.
- **Free cloud**:
  - **Replit**: Paste the project, enable "Always On"
  - **Render.com**: Create a Worker, start with `python main.py`