import re
from typing import List, Dict

SKILL_SYNONYMS: Dict[str, str] = {
    # Programming languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "golang": "Go",
    "go": "Go",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "java": "Java",
    "ruby": "Ruby",
    "php": "PHP",
    "rust": "Rust",
    
    # Frameworks
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "vue": "Vue.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "express.js": "Express",
    "expressjs": "Express",
    "express": "Express",
    "django": "Django",
    "django rest": "Django",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    
    # ML/AI
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "llm": "Large Language Models",
    "large language models": "Large Language Models",
    "gen ai": "Generative AI",
    "generative ai": "Generative AI",
    "langchain": "LangChain",
    "sklearn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    
    # Cloud/DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "github actions": "GitHub Actions",
    "terraform": "Terraform",
    "ansible": "Ansible",
    
    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elastic": "Elasticsearch",
    "elasticsearch": "Elasticsearch",
    "sqlite": "SQLite",
    "dynamodb": "DynamoDB"
}

def normalize_skill(skill: str) -> str:
    """
    Normalizes a single skill string to its canonical form.
    """
    clean_skill = skill.lower().strip()
    if clean_skill in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[clean_skill]
    return skill.strip().title()

def normalize_skills(skills: List[str]) -> List[str]:
    """
    Normalizes a list of skills, removes duplicates, and filters short strings.
    """
    normalized = []
    seen = set()
    for s in skills:
        n = normalize_skill(s)
        if len(n) >= 2 and n.lower() not in seen:
            normalized.append(n)
            seen.add(n.lower())
    return normalized

def extract_skill_keywords(text: str) -> List[str]:
    """
    Fallback regex-based skill extraction from raw text by matching against known synonyms.
    """
    found_skills = []
    text_lower = text.lower()
    
    # Match against the keys of our synonym dictionary
    for synonym in SKILL_SYNONYMS.keys():
        # Use word boundaries to avoid partial matches (e.g., 'go' in 'good')
        pattern = rf'\b{re.escape(synonym)}\b'
        if re.search(pattern, text_lower):
            found_skills.append(SKILL_SYNONYMS[synonym])
            
    return normalize_skills(found_skills)
