from typing import List, Dict, Any

LEARNING_RESOURCES = {
    "Python": {
        "level": "beginner",
        "resources": [
            {"type": "course", "name": "Python for Everybody", "platform": "Coursera", "url": "https://coursera.org/learn/python"},
            {"type": "docs", "name": "Official Python Tutorial", "platform": "python.org", "url": "https://docs.python.org/3/tutorial/"},
            {"type": "practice", "name": "LeetCode Python", "platform": "LeetCode", "url": "https://leetcode.com"}
        ],
        "estimated_weeks": 4
    },
    "Docker": {
        "level": "intermediate",
        "resources": [
            {"type": "course", "name": "Docker Mastery", "platform": "Udemy", "url": "https://udemy.com"},
            {"type": "docs", "name": "Docker Getting Started", "platform": "Docker Docs", "url": "https://docs.docker.com/get-started/"},
            {"type": "practice", "name": "Play with Docker", "platform": "PWD", "url": "https://labs.play-with-docker.com"}
        ],
        "estimated_weeks": 2
    },
    "AWS": {
        "level": "intermediate",
        "resources": [
            {"type": "course", "name": "AWS Cloud Practitioner Essentials", "platform": "AWS Skill Builder", "url": "https://explore.skillbuilder.aws/"},
            {"type": "certification", "name": "AWS Solutions Architect", "platform": "A Cloud Guru", "url": "https://acloudguru.com"}
        ],
        "estimated_weeks": 6
    },
    "FastAPI": {
        "level": "intermediate",
        "resources": [
            {"type": "docs", "name": "FastAPI Documentation", "platform": "fastapi.tiangolo.com", "url": "https://fastapi.tiangolo.com/"},
            {"type": "course", "name": "Full Stack FastAPI", "platform": "TestDriven.io", "url": "https://testdriven.io/courses/fastapi-celery/"}
        ],
        "estimated_weeks": 2
    },
    "SQL": {
        "level": "beginner",
        "resources": [
            {"type": "course", "name": "SQL for Data Science", "platform": "Coursera", "url": "https://coursera.org/learn/sql-for-data-science"},
            {"type": "practice", "name": "SQLZoo", "platform": "SQLZoo", "url": "https://sqlzoo.net/"}
        ],
        "estimated_weeks": 3
    },
    "Machine Learning": {
        "level": "intermediate",
        "resources": [
            {"type": "course", "name": "Machine Learning Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
            {"type": "practice", "name": "Kaggle Learn", "platform": "Kaggle", "url": "https://www.kaggle.com/learn"}
        ],
        "estimated_weeks": 10
    },
    "Kubernetes": {
        "level": "advanced",
        "resources": [
            {"type": "course", "name": "Certified Kubernetes Administrator (CKA)", "platform": "Mumshad Mannambeth", "url": "https://kodekloud.com/"},
            {"type": "docs", "name": "K8s Documentation", "platform": "kubernetes.io", "url": "https://kubernetes.io/docs/home/"}
        ],
        "estimated_weeks": 8
    },
    "React": {
        "level": "intermediate",
        "resources": [
            {"type": "course", "name": "The Joy of React", "platform": "Josh W. Comeau", "url": "https://www.joyofreact.com/"},
            {"type": "docs", "name": "React Documentation", "platform": "react.dev", "url": "https://react.dev/"}
        ],
        "estimated_weeks": 4
    },
    "TypeScript": {
        "level": "intermediate",
        "resources": [
            {"type": "course", "name": "Total TypeScript", "platform": "Matt Pocock", "url": "https://www.totaltypescript.com/"},
            {"type": "docs", "name": "TypeScript Handbook", "platform": "typescriptlang.org", "url": "https://www.typescriptlang.org/docs/"}
        ],
        "estimated_weeks": 2
    },
    "PostgreSQL": {
        "level": "intermediate",
        "resources": [
            {"type": "course", "name": "Mastering PostgreSQL", "platform": "Udemy", "url": "https://udemy.com"},
            {"type": "docs", "name": "Postgres Documentation", "platform": "postgresql.org", "url": "https://www.postgresql.org/docs/"}
        ],
        "estimated_weeks": 3
    },
    "Redis": {
        "level": "intermediate",
        "resources": [
            {"type": "course", "name": "Redis University", "platform": "Redis", "url": "https://university.redis.com/"}
        ],
        "estimated_weeks": 1
    },
    "LangChain": {
        "level": "advanced",
        "resources": [
            {"type": "course", "name": "LangChain for LLM Application Development", "platform": "DeepLearning.AI", "url": "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/"}
        ],
        "estimated_weeks": 2
    },
    "PyTorch": {
        "level": "advanced",
        "resources": [
            {"type": "course", "name": "PyTorch for Deep Learning", "platform": "Udacity", "url": "https://www.udacity.com/course/deep-learning-pytorch--ud188"},
            {"type": "docs", "name": "PyTorch Tutorials", "platform": "pytorch.org", "url": "https://pytorch.org/tutorials/"}
        ],
        "estimated_weeks": 6
    },
    "MLflow": {
        "level": "intermediate",
        "resources": [
            {"type": "docs", "name": "MLflow Documentation", "platform": "mlflow.org", "url": "https://mlflow.org/docs/latest/index.html"}
        ],
        "estimated_weeks": 1
    },
    "Qdrant": {
        "level": "intermediate",
        "resources": [
            {"type": "docs", "name": "Qdrant Documentation", "platform": "qdrant.tech", "url": "https://qdrant.tech/documentation/"}
        ],
        "estimated_weeks": 1
    },
    "CI/CD": {
        "level": "intermediate",
        "resources": [
            {"type": "course", "name": "GitHub Actions Tutorial", "platform": "YouTube", "url": "https://youtube.com"}
        ],
        "estimated_weeks": 2
    }
}

def normalize_skill_for_lookup(skill: str) -> str:
    """Try to match messy skill names to known resources (Bug 4 fix)"""
    skill_lower = skill.lower()
    
    # Direct mappings for common patterns
    if "python" in skill_lower: return "Python"
    if "sql" in skill_lower and "nosql" not in skill_lower: return "SQL"
    if "nosql" in skill_lower or "mongodb" in skill_lower or "mongo" in skill_lower: return "MongoDB"
    if "machine learning" in skill_lower or "ml model" in skill_lower: return "Machine Learning"
    if "statistical" in skill_lower: return "Python"  # Pandas/scipy
    if "hypothesis" in skill_lower: return "Python"
    if "deep learning" in skill_lower: return "PyTorch"
    if "docker" in skill_lower: return "Docker"
    if "kubernetes" in skill_lower or "k8s" in skill_lower: return "Kubernetes"
    if "aws" in skill_lower or "amazon" in skill_lower: return "AWS"
    if "react" in skill_lower: return "React"
    if "fastapi" in skill_lower: return "FastAPI"
    if "langchain" in skill_lower: return "LangChain"
    if "redis" in skill_lower: return "Redis"
    if "postgres" in skill_lower: return "PostgreSQL"
    
    return skill  # return original if no match

def generate_learning_path(
    missing_skills: List[str],
    preferred_missing: List[str],
    jd_role: str
) -> Dict[str, Any]:
    """
    Generates a structured learning path based on missing skills.
    """
    priority_skills = []
    secondary_skills = []
    total_weeks = 0
    recommended_order = []
    
    # Process required missing skills first
    for raw_skill in missing_skills:
        skill = normalize_skill_for_lookup(raw_skill)
        resource_data = LEARNING_RESOURCES.get(skill)
        
        if not resource_data:
            # Fallback for unknown skills - Bug 4 fix (YouTube instead of Google)
            resource_data = {
                "level": "unknown",
                "resources": [
                    {
                        "type": "search", 
                        "name": f"Learn {raw_skill} Tutorial", 
                        "platform": "YouTube", 
                        "url": f"https://www.youtube.com/results?search_query=learn+{raw_skill.replace(' ', '+')}+tutorial"
                    }
                ],
                "estimated_weeks": 2
            }
            
        skill_entry = {
            "skill": raw_skill, # Keep original name for display
            "level": resource_data["level"],
            "resources": resource_data["resources"],
            "estimated_weeks": resource_data["estimated_weeks"]
        }
        
        if len(priority_skills) < 3:
            priority_skills.append(skill_entry)
            recommended_order.append(raw_skill)
            total_weeks += resource_data["estimated_weeks"]
        else:
            secondary_skills.append(skill_entry)
            
    # Process preferred missing skills
    for raw_skill in preferred_missing:
        skill = normalize_skill_for_lookup(raw_skill)
        resource_data = LEARNING_RESOURCES.get(skill)
        if not resource_data:
            resource_data = {
                "level": "unknown",
                "resources": [
                    {
                        "type": "search", 
                        "name": f"Learn {raw_skill}", 
                        "platform": "YouTube", 
                        "url": f"https://www.youtube.com/results?search_query=learn+{raw_skill.replace(' ', '+')}"
                    }
                ],
                "estimated_weeks": 1
            }
            
        secondary_skills.append({
            "skill": raw_skill,
            "level": resource_data["level"],
            "resources": resource_data["resources"],
            "estimated_weeks": resource_data["estimated_weeks"]
        })

    summary = ""
    if priority_skills:
        top_skills = ", ".join([s["skill"] for s in priority_skills[:2]])
        summary = f"Focus on {top_skills} first — they are critical requirements for the {jd_role} role."
    else:
        summary = f"You match all core requirements for {jd_role}! Consider learning preferred skills to stand out."
        
    return {
        "priority_skills": priority_skills,
        "secondary_skills": secondary_skills,
        "total_estimated_weeks": total_weeks,
        "recommended_order": recommended_order,
        "summary": summary
    }
