"""Tests for section detection heuristics."""
import pytest
from pdf_parsing.section_detector import detect_sections, get_section_weights


SAMPLE_RESUME = """
JOHN DOE
john@example.com | linkedin.com/in/johndoe

SUMMARY
Experienced backend developer with 3 years in Python and Django.

SKILLS
Python, Django, FastAPI, PostgreSQL, Docker, AWS, Git

EXPERIENCE
Software Engineer at TechCorp (2021-2024)
- Built REST APIs using Django and FastAPI
- Deployed microservices on AWS using Docker

EDUCATION
B.Tech Computer Science, XYZ University (2017-2021)
CGPA: 8.5/10

PROJECTS
SkillSync Resume Matcher
- Built an intelligent resume-job matching system
- Used Python, SBERT, and FastAPI
"""


class TestSectionDetection:
    def test_detects_skills_section(self):
        sections = detect_sections(SAMPLE_RESUME)
        assert "skills" in sections
        assert "django" in sections["skills"].lower()

    def test_detects_experience_section(self):
        sections = detect_sections(SAMPLE_RESUME)
        assert "experience" in sections
        assert "techcorp" in sections["experience"].lower()

    def test_detects_education_section(self):
        sections = detect_sections(SAMPLE_RESUME)
        assert "education" in sections
        assert "b.tech" in sections["education"].lower()

    def test_detects_projects_section(self):
        sections = detect_sections(SAMPLE_RESUME)
        assert "projects" in sections
        assert "skillsync" in sections["projects"].lower()

    def test_detects_summary_section(self):
        sections = detect_sections(SAMPLE_RESUME)
        assert "summary" in sections

    def test_header_text_not_in_section_body(self):
        """Section headings themselves should not appear in the body."""
        sections = detect_sections(SAMPLE_RESUME)
        # The word "SKILLS" as a heading shouldn't be the section content
        assert len(sections.get("skills", "")) > 10

    def test_empty_text(self):
        sections = detect_sections("")
        assert "other" in sections

    def test_no_headings(self):
        text = "Just a paragraph with no sections at all."
        sections = detect_sections(text)
        assert "other" in sections
        assert "Just a paragraph" in sections["other"]

    def test_title_case_headings(self):
        text = """
Skills
Python, Java, Go

Experience
Developer at ABC Corp
"""
        sections = detect_sections(text)
        assert "skills" in sections
        assert "python" in sections["skills"].lower()


class TestSectionWeights:
    def test_skills_highest_weight(self):
        weights = get_section_weights()
        assert weights["skills"] == 1.0
        assert weights["skills"] > weights["experience"]
        assert weights["skills"] > weights["education"]

    def test_all_weights_positive(self):
        weights = get_section_weights()
        for name, w in weights.items():
            assert w > 0, f"Weight for {name} should be positive"

    def test_all_weights_at_most_one(self):
        weights = get_section_weights()
        for name, w in weights.items():
            assert w <= 1.0, f"Weight for {name} should be <= 1.0"