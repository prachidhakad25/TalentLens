import unittest
from backend.app.matching import calculate_match, rank_candidates

class MatchingTests(unittest.TestCase):
    def test_skill_and_project_evidence(self):
        student = {
            "skills": ["Python", "SQL"],
            "projects": [{"title": "Sales dashboard", "technologies": ["Pandas", "Power BI"]}],
            "github_languages": ["Python"],
            "degree": "B.Tech Computer Science",
            "experience_years": 1,
            "preferred_location": "Remote",
            "remote_preference": True,
        }
        job = {
            "title": "Data Analyst Intern",
            "required_skills": ["Python", "SQL", "Pandas"],
            "preferred_skills": ["Power BI"],
            "degree": "B.Tech",
            "experience_min": 0,
            "location": "Remote",
            "remote": True,
        }
        result = calculate_match(student, job)
        self.assertEqual(result["matched_skills"], ["pandas", "python", "sql"])
        self.assertEqual(result["missing_skills"], [])
        self.assertGreater(result["match_score"], 70)
        self.assertIn("not a probability", result["score_note"])

    def test_ranking_order(self):
        job = {"title": "Python Developer", "required_skills": ["Python"], "remote": True}
        people = [{"name": "A", "skills": []}, {"name": "B", "skills": ["Python"], "projects": []}]
        ranked = rank_candidates(people, job)
        self.assertEqual(ranked[0]["student"]["name"], "B")
        self.assertEqual([x["rank"] for x in ranked], [1, 2])

if __name__ == "__main__":
    unittest.main()
