class TitleCanonicalizer:
    title_map = {
        "software developer": "Software Engineer",
        "backend engineer": "Software Engineer",
        "frontend engineer": "Software Engineer",
        "sr software engineer": "Senior Software Engineer"
    }

    @staticmethod
    def canonicalize(title: str) -> str:
        clean_title = title.strip().lower()
        return TitleCanonicalizer.title_map.get(clean_title, title.strip())