from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import string

# Load the spaCy model for text preprocessing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    """Cleans and preprocesses text using spaCy."""
    stop_words = spacy.lang.en.stop_words.STOP_WORDS
    doc = nlp(text.lower())
    tokens = [
        token.lemma_
        for token in doc
        if token.text not in string.punctuation and token.text not in stop_words and not token.is_space
    ]
    return " ".join(tokens)

def calculate_similarity(resume_text, job_description_text):
    """Calculates cosine similarity between two texts after preprocessing."""
    if not resume_text or not job_description_text:
        return 0.0

    # Preprocess both texts
    processed_resume = preprocess_text(resume_text)
    processed_jd = preprocess_text(job_description_text)
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([processed_resume, processed_jd])
    
    # Calculate cosine similarity
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    return round(similarity_score * 100, 2)