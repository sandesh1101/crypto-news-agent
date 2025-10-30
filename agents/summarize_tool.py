from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from transformers.utils import logging

# Reduce verbosity of transformers logging
logging.set_verbosity_error()

# Initialize the summarization pipeline
SUMMARIZER = None

def load_summarizer():
    global SUMMARIZER
    if SUMMARIZER is None:
        try:
            # Using a small, fast model for summarization
            model_name = "facebook/bart-large-cnn"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            SUMMARIZER = pipeline("summarization", model=model, tokenizer=tokenizer)
        except Exception as e:
            print(f"Error loading summarization model: {str(e)}")
            raise

def summarize_article(url: str) -> str:
    """
    Fetches the full text of a news article from a URL and generates a concise summary
    using the Hugging Face BART model.
    
    Args:
        url (str): The URL of the article to summarize.
        
    Returns:
        str: A 3-5 line summary of the article's key points.
    """
    try:
        # Fetch the article content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML content with html5lib for better compatibility
        soup = BeautifulSoup(response.text, 'html5lib')
        
        # Remove script, style, and other non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript", "button", "form"]):
            element.decompose()
            
        # Get text from paragraphs and clean it up
        paragraphs = []
        for p in soup.find_all(['p', 'h1', 'h2', 'h3']):
            text = p.get_text(strip=True)
            if len(text.split()) > 10:  # Only include non-empty paragraphs
                paragraphs.append(text)
        
        if not paragraphs:
            return "Could not extract article content. The page may require JavaScript to load content."
        
        # Join paragraphs and clean up text
        text = ' '.join(paragraphs)
        text = ' '.join(text.split())  # Normalize whitespace
        
        # Load the summarizer if not already loaded
        if SUMMARIZER is None:
            load_summarizer()
        
        # Truncate text to fit model's max length (1024 tokens for BART)
        max_chars = 4000  # Conservative estimate to fit within 1024 tokens
        if len(text) > max_chars:
            text = text[:max_chars]
        
        # Generate summary
        summary = SUMMARIZER(
            text,
            max_length=130,
            min_length=30,
            do_sample=False,
            truncation=True,
            no_repeat_ngram_size=3
        )
        
        return summary[0]['summary_text'].strip()
        
    except requests.RequestException as e:
        return f"Error fetching article: {str(e)}"
    except Exception as e:
        # Fallback to extractive summarization if abstractive fails
        try:
            # Simple extractive summarization (first few sentences)
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            return '. '.join(sentences[:3]) + '.'
        except Exception as e2:
            return f"Error generating summary: {str(e2)[:200]}..."
