import re

class SkillCanonicalizer:
    skill_map = {
        "python3": "Python",
        "js": "JavaScript",
        "ml": "Machine Learning",
        "react.js": "React",
        "node.js": "Node.js",
        "aws": "Amazon Web Services"
    }

    @staticmethod
    def canonicalize(skill: str) -> str:
        clean_skill = skill.strip().lower()
        return SkillCanonicalizer.skill_map.get(clean_skill, skill.strip())