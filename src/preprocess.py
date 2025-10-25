import unicodedata
import re

def normalize(text):
    """Normalize text input for LLM analysis."""
    text = unicodedata.normalize('NFKC', text)
    # Remove excess whitespace, high Unicode
    text = re.sub(r'[\u2000-\u206F]', '', text)
    text = ' '.join(text.split())
    return text

if __name__ == '__main__':
    sample = "H̷e̴l̴l̶o̴, jailbreak! "
    print(normalize(sample))
