import re
import spacy
import docx
import fitz  

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    
#  A predefined list of technical skills for better extraction 
SKILLS_DB = [
    'python', 'java', 'c++', 'javascript', 'typescript', 'sql', 'nosql', 'git', 'docker', 'kubernetes', 'aws',
    'azure', 'gcp', 'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring boot', 'node.js',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
    'data analysis', 'data visualization', 'restful api', 'api design', 'microservices', 'agile', 'scrum',
    'project management', 'product management', 'ui/ux', 'figma', 'jira', 'ci/cd', 'devops', 'testing'
]

def extract_text_from_file(file):
    """Extracts text from uploaded file (PDF or DOCX)."""
    text = ""
    try:
        if file.type == "application/pdf":
            # For PDF, read bytes and open with fitz
            file.seek(0)
            doc = fitz.open(stream=file.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # For DOCX, open with python-docx
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"Error reading file {file.name}: {e}")
    return text

def extract_contact_info(text):
    """Extracts name, email, and phone number from text."""
    info = {'name': None, 'email': None, 'phone': None}
    
    # Extract Name using spaCy's Named Entity Recognition (NER)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            info['name'] = ent.text
            break # Take the first person's name found
            
    # Extract Email using regex
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        info['email'] = email_match.group(0)
        
    # Extract Phone number using regex
    phone_match = re.search(r'(\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?\d{4})', text)
    if phone_match:
        info['phone'] = phone_match.group(0)
        
    return info

def extract_skills(text):
    """Extracts skills from text based on the SKILLS_DB."""
    doc = nlp(text.lower())
    found_skills = []
    
    # Check for direct matches in the skills database
    for skill in SKILLS_DB:
        if skill in text.lower():
            found_skills.append(skill)
            
    # Use lemmatization to find skill variations
    for token in doc:
        if token.lemma_ in SKILLS_DB and token.lemma_ not in found_skills:
            found_skills.append(token.lemma_)
            
    return list(set(found_skills)) # Return unique skills
