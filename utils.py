import os
import re
import logging
from datetime import datetime
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def clean_text(text):
    """
    Clean and normalize text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\?\!]', '', text)

    return text

def format_date(date_str):
    """
    Attempt to format various date strings to a standard format
    """
    try:
        # Try various date formats
        date_formats = [
            '%Y-%m-%dT%H:%M:%S', 
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%B %d, %Y',
            '%d %B %Y',
            '%a, %d %b %Y %H:%M:%S'
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # If no format matches, return the original string
        return date_str
    except Exception as e:
        logger.error(f"Error formatting date {date_str}: {e}")
        return date_str

def generate_cache_key(company_name):
    """
    Generate a cache key for storing fetched news data
    """
    return f"{company_name.lower().replace(' ', '')}{datetime.now().strftime('%Y%m%d')}"

def calculate_reading_time(text):
    """
    Calculate estimated reading time in minutes
    """
    # Average reading speed: 200-250 words per minute
    words = len(text.split())
    minutes = words / 200

    if minutes < 1:
        return "Less than a minute"
    elif minutes < 2:
        return "About 1 minute"
    else:
        return f"About {int(minutes)} minutes"

def truncate_text(text, max_length=100):
    """
    Truncate text to max_length and add ellipsis
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(' ', 1)[0] + '...'

def save_to_json(data, filename):
    """
    Save data to a JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        return False

def load_from_json(filename):
    """
    Load data from a JSON file
    """
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading from JSON: {e}")
        return None

def create_cache_dir():
    """
    Create a cache directory if it doesn't exist
    """
    cache_dir = 'cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir

def get_cached_data(company_name, max_age_hours=6):
    """
    Get cached data for a company if available and not too old
    """
    cache_dir = create_cache_dir()
    cache_key = generate_cache_key(company_name)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")

    if os.path.exists(cache_file):
        # Check file age
        file_time = os.path.getmtime(cache_file)
        age_hours = (datetime.now().timestamp() - file_time) / 3600

        if age_hours <= max_age_hours:
            return load_from_json(cache_file)

    return None

def predict_stock_trend(sentiment_counts, avg_sentiment_score):
    """
    Predict potential stock trend based on sentiment analysis
    """
    total = sum(sentiment_counts.values())
    if total == 0:
        return "Unclear market impact"
    
    positive_ratio = sentiment_counts.get("Positive", 0) / total
    negative_ratio = sentiment_counts.get("Negative", 0) / total
    
    if positive_ratio > 0.6:
        return "Potential stock growth expected"
    elif positive_ratio > 0.4:
        return "Slight positive market reaction possible"
    elif negative_ratio > 0.6:
        return "Potential stock decline expected"
    elif negative_ratio > 0.4:
        return "Slight negative market reaction possible"
    else:
        return "Stable market performance expected"