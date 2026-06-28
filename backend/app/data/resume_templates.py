"""Built-in resume HTML/CSS templates (seeded as system templates)."""

CLASSIC_BODY = """
<h1>{{ resume.basic_details.full_name or 'Candidate' }}</h1>
<div class="contact">
  {% if resume.basic_details.email %}{{ resume.basic_details.email }}{% endif %}
  {% if resume.basic_details.phone %} · {{ resume.basic_details.phone }}{% endif %}
  {% if resume.basic_details.location %} · {{ resume.basic_details.location }}{% endif %}
</div>
{% if resume.summary %}
<h2>Summary</h2>
<p class="summary">{{ resume.summary }}</p>
{% endif %}
{% if resume.experience %}
<h2>Experience</h2>
{% for exp in resume.experience %}
<p><span class="job-title">{{ exp.title }}</span> — <span class="job-company">{{ exp.company }}</span>
  {% if exp.start_date %} ({{ exp.start_date }} – {{ exp.end_date or 'Present' }}){% endif %}
</p>
<ul>{% for bullet in exp.bullets %}<li>{{ bullet }}</li>{% endfor %}</ul>
{% endfor %}
{% endif %}
{% if resume.skills %}
<h2>Skills</h2>
<div class="skills">{% for skill in resume.skills %}<span class="skill-tag">{{ skill }}</span>{% endfor %}</div>
{% endif %}
{% if resume.education %}
<h2>Education</h2>
{% for edu in resume.education %}
<p>{{ edu.degree }}{% if edu.field %}, {{ edu.field }}{% endif %} — {{ edu.institution }}
  {% if edu.graduation_year %} ({{ edu.graduation_year }}){% endif %}
</p>
{% endfor %}
{% endif %}
"""

CLASSIC_CSS = """
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a2e; margin: 40px; line-height: 1.5; }
h1 { font-size: 28px; margin-bottom: 4px; color: #16213e; }
.contact { color: #555; font-size: 13px; margin-bottom: 20px; }
h2 { font-size: 16px; color: #0f3460; border-bottom: 2px solid #0f3460; padding-bottom: 4px; margin-top: 24px; }
.summary { margin: 12px 0; }
.job-title { font-weight: 600; }
.job-company { color: #555; }
ul { margin: 6px 0 16px 0; padding-left: 20px; }
li { margin-bottom: 4px; }
.skills { display: flex; flex-wrap: wrap; gap: 6px; }
.skill-tag { background: #e8eaf6; padding: 4px 10px; border-radius: 4px; font-size: 13px; }
"""

MODERN_BODY = """
<div class="header">
  <h1>{{ resume.basic_details.full_name or 'Candidate' }}</h1>
  <div class="contact">
    {% if resume.basic_details.email %}{{ resume.basic_details.email }}{% endif %}
    {% if resume.basic_details.phone %} · {{ resume.basic_details.phone }}{% endif %}
    {% if resume.basic_details.location %} · {{ resume.basic_details.location }}{% endif %}
  </div>
</div>
<div class="content">
{% if resume.summary %}
<h2>Summary</h2>
<p>{{ resume.summary }}</p>
{% endif %}
{% if resume.experience %}
<h2>Experience</h2>
{% for exp in resume.experience %}
<div class="exp-block">
  <div class="exp-head"><strong>{{ exp.title }}</strong> @ {{ exp.company }}
    <span class="dates">{% if exp.start_date %}{{ exp.start_date }} – {{ exp.end_date or 'Present' }}{% endif %}</span>
  </div>
  <ul>{% for bullet in exp.bullets %}<li>{{ bullet }}</li>{% endfor %}</ul>
</div>
{% endfor %}
{% endif %}
{% if resume.skills %}
<h2>Skills</h2>
<div class="skills">{% for skill in resume.skills %}<span>{{ skill }}</span>{% endfor %}</div>
{% endif %}
{% if resume.education %}
<h2>Education</h2>
{% for edu in resume.education %}
<p><strong>{{ edu.degree }}</strong> — {{ edu.institution }}{% if edu.graduation_year %} ({{ edu.graduation_year }}){% endif %}</p>
{% endfor %}
{% endif %}
</div>
"""

MODERN_CSS = """
body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; color: #222; line-height: 1.5; }
.header { background: #1e3a5f; color: #fff; padding: 32px 40px; }
.header h1 { margin: 0 0 8px; font-size: 30px; }
.header .contact { font-size: 14px; opacity: 0.9; }
.content { padding: 32px 40px; }
h2 { font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #1e3a5f; margin-top: 28px; margin-bottom: 12px; }
.exp-block { margin-bottom: 16px; }
.exp-head { margin-bottom: 6px; }
.dates { float: right; color: #666; font-size: 13px; }
.skills span { display: inline-block; background: #eef2f7; padding: 4px 10px; margin: 4px; border-radius: 4px; font-size: 13px; }
ul { padding-left: 18px; margin: 0; }
"""

MINIMAL_BODY = """
<h1>{{ resume.basic_details.full_name or 'Candidate' }}</h1>
<p class="meta">
  {% if resume.basic_details.email %}{{ resume.basic_details.email }}{% endif %}
  {% if resume.basic_details.phone %} | {{ resume.basic_details.phone }}{% endif %}
</p>
{% if resume.summary %}<p class="lead">{{ resume.summary }}</p>{% endif %}
{% if resume.experience %}
<h2>Experience</h2>
{% for exp in resume.experience %}
<p><b>{{ exp.title }}</b>, {{ exp.company }}
  {% if exp.start_date %}<em>({{ exp.start_date }} – {{ exp.end_date or 'Present' }})</em>{% endif %}
</p>
<ul>{% for bullet in exp.bullets %}<li>{{ bullet }}</li>{% endfor %}</ul>
{% endfor %}
{% endif %}
{% if resume.skills %}<h2>Skills</h2><p>{{ resume.skills | join(', ') }}</p>{% endif %}
{% if resume.education %}
<h2>Education</h2>
{% for edu in resume.education %}
<p>{{ edu.degree }}, {{ edu.institution }}{% if edu.graduation_year %} — {{ edu.graduation_year }}{% endif %}</p>
{% endfor %}
{% endif %}
"""

MINIMAL_CSS = """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 700px; margin: 48px auto; padding: 0 24px; color: #111; }
h1 { font-size: 32px; font-weight: normal; margin-bottom: 4px; }
.meta { color: #555; font-size: 14px; margin-bottom: 24px; }
.lead { font-size: 15px; margin-bottom: 20px; }
h2 { font-size: 13px; font-weight: bold; margin-top: 24px; border-top: 1px solid #ccc; padding-top: 8px; }
ul { margin: 8px 0 16px; }
"""

SYSTEM_TEMPLATES = [
    {
        "name": "Classic Professional",
        "description": "Clean serif layout with navy section headers — good for corporate roles.",
        "html_template": CLASSIC_BODY.strip(),
        "css_styles": CLASSIC_CSS.strip(),
        "is_default": True,
    },
    {
        "name": "Modern Header",
        "description": "Bold colored header band with structured experience blocks.",
        "html_template": MODERN_BODY.strip(),
        "css_styles": MODERN_CSS.strip(),
        "is_default": False,
    },
    {
        "name": "Minimal Serif",
        "description": "Simple typography-focused layout for executive and academic profiles.",
        "html_template": MINIMAL_BODY.strip(),
        "css_styles": MINIMAL_CSS.strip(),
        "is_default": False,
    },
]

SAMPLE_RESUME_JSON = {
    "basic_details": {
        "full_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+1 555-0100",
        "location": "San Francisco, CA",
    },
    "summary": "Senior software engineer with 8+ years building scalable APIs and cloud platforms.",
    "experience": [
        {
            "company": "TechCorp",
            "title": "Senior Software Engineer",
            "start_date": "2020",
            "end_date": "Present",
            "is_current": True,
            "bullets": [
                "Led team of 5 engineers delivering FastAPI microservices",
                "Reduced API latency by 40% through caching and query optimization",
            ],
        },
        {
            "company": "StartupXYZ",
            "title": "Software Engineer",
            "start_date": "2017",
            "end_date": "2020",
            "is_current": False,
            "bullets": ["Built React dashboards used by 50k+ users"],
        },
    ],
    "skills": ["Python", "FastAPI", "PostgreSQL", "React", "AWS", "Docker"],
    "education": [
        {
            "institution": "State University",
            "degree": "B.S. Computer Science",
            "field": "Computer Science",
            "graduation_year": "2017",
        },
    ],
}
