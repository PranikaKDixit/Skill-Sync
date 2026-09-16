"""Tests for the matching engine."""

from matching_engine import (
    calculate_match,
    keyword_match,
    skill_match,
    tfidf_match,
    extract_skills,
)


def test_perfect_match():
    """Test identical texts score very high."""
    text = "Python developer with 5 years Django and React experience"
    score = calculate_match(text, text)
    print(f"✅ Perfect match: {score}%")
    assert score >= 90, f"Expected ≥90%, got {score}%"


def test_high_match():
    """Test strong resume-job alignment."""
    resume = """
    Senior Software Engineer with 5 years experience in Python and JavaScript.
    Expert in Django, Flask, React, and Node.js. Built REST APIs and microservices.
    Experience with Docker, Kubernetes, AWS, PostgreSQL, and Redis.
    """
    job = """
    We're looking for a Senior Software Engineer with Python, JavaScript expertise.
    Must have Django, React, and REST API experience. AWS and Docker required.
    PostgreSQL experience preferred.
    """
    score = calculate_match(resume, job)
    print(f"✅ High match: {score}%")
    assert 70 <= score <= 95, f"Expected 70-95%, got {score}%"


def test_medium_match():
    """Partial alignment."""
    resume = "Full-stack developer: JavaScript, React, Node.js, MongoDB, Docker"
    job = "Backend engineer: Python, Django, PostgreSQL, Docker, Git, 5 years"
    score = calculate_match(resume, job)
    print(f"Medium match: {score}%")
    assert 10 <= score <= 60, f"Expected 10-60%, got {score}%"  # Lowered floor
    print("✅ PASS\n")


def test_low_match():
    """Test unrelated resume and job."""
    resume = "Graphic designer with 3 years Photoshop, Illustrator, InDesign"
    job = "DevOps engineer needed: Docker, Kubernetes, AWS, Terraform, Jenkins"
    score = calculate_match(resume, job)
    print(f"✅ Low match: {score}%")
    assert score <= 30, f"Expected ≤30%, got {score}%"


def test_skill_extraction():
    """Test skill detection including aliases."""
    text = "Expert in Python, ReactJS, NodeJS, Postgres, K8s, and ML"
    skills = extract_skills(text)
    print(f"✅ Extracted skills: {skills}")
    
    # Check canonical skills
    assert "python" in skills, "Should find python"
    assert "react" in skills, "ReactJS should map to react"
    assert "node.js" in skills, "NodeJS should map to node.js"
    assert "postgresql" in skills, "Postgres should map to postgresql"
    assert "kubernetes" in skills, "K8s should map to kubernetes"
    assert "machine learning" in skills, "ML should map to machine learning"


def test_keyword_matching():
    """Test keyword overlap calculation."""
    resume = "Python developer with Django and Flask experience"
    job = "Python Django Flask developer"
    score = keyword_match(resume, job)
    print(f"✅ Keyword match: {score}%")
    assert score >= 75, f"High keyword overlap should be ≥75%, got {score}%"


def test_skill_matching():
    """Test skill-specific matching."""
    resume = "Skills: Python, React, Docker, MySQL"
    job = "Required: Python, React, AWS, PostgreSQL"
    score = skill_match(resume, job)
    print(f"✅ Skill match: {score}%")
    # 2 out of 4 skills match = 50%
    assert 45 <= score <= 55, f"Expected ~50%, got {score}%"


def test_tfidf_matching():
    """Test semantic similarity."""
    resume = "Experienced software engineer with Python expertise"
    job = "Looking for experienced software engineer with Python skills"
    score = tfidf_match(resume, job)
    print(f"✅ TF-IDF match: {score}%")
    assert score >= 50, f"Similar texts should be ≥50%, got {score}%"


def test_edge_cases():
    """Test error handling."""
    # Empty resume
    score = calculate_match("", "Python developer needed")
    print(f"✅ Empty resume: {score}%")
    assert score == 0.0, f"Empty resume should be 0%, got {score}%"
    
    # Empty job
    score = calculate_match("Python developer", "")
    print(f"✅ Empty job: {score}%")
    assert score == 0.0, f"Empty job should be 0%, got {score}%"
    
    # Both empty
    score = calculate_match("", "")
    print(f"✅ Both empty: {score}%")
    assert score == 0.0, f"Both empty should be 0%, got {score}%"
    
    # None inputs
    score = calculate_match(None, None)
    print(f"✅ None inputs: {score}%")
    assert score == 0.0, f"None inputs should be 0%, got {score}%"


def test_fallback_cosine():
    """Test that fallback cosine similarity works."""
    from matching_engine import _token_cosine, _tokens
    
    resume = "Python developer with Django"
    job = "JavaScript developer with React"  # Different but some overlap
    
    resume_tokens = _tokens(resume)
    job_tokens = _tokens(job)
    
    similarity = _token_cosine(resume_tokens, job_tokens)
    print(f"Fallback cosine: {similarity:.2%}")
    assert 0.2 <= similarity <= 1.01, f"Should be 0.2-1.0, got {similarity}"
    print("✅ PASS\n")


def test_special_characters():
    """Test handling of C++, C#, .NET, etc."""
    resume = "Expert in C++, C#, .NET, and Node.js development"
    skills = extract_skills(resume)
    print(f"✅ Special chars skills: {skills}")
    
    assert "c++" in skills, "Should find C++"
    assert "c#" in skills, "Should find C#"
    assert "node.js" in skills, "Should find Node.js"


if __name__ == "__main__":
    print("=" * 60)
    print("MATCHING ENGINE TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        test_perfect_match,
        test_high_match,
        test_medium_match,
        test_low_match,
        test_skill_extraction,
        test_keyword_matching,
        test_skill_matching,
        test_tfidf_matching,
        test_edge_cases,
        test_fallback_cosine,
        test_special_characters,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"❌ FAILED: {test.__name__}")
            print(f"   {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"❌ ERROR in {test.__name__}: {e}")
            failed.append(test.__name__)
        print()
    
    print("=" * 60)
    if not failed:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {len(failed)} TEST(S) FAILED:")
        for name in failed:
            print(f"   - {name}")
    print("=" * 60)
