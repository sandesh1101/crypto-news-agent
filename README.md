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
- **GitHub Actions**: This project is hosted using **GitHub Actions**, which automatically runs the agent every day at **7 AM** to fetch the latest crypto or stock news. The workflow installs dependencies, runs `main.py`, and exits within a few minutes. No external hosting is needed — GitHub Actions handles scheduling and execution for free.
