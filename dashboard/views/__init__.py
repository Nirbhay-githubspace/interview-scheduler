from .home import render_home_page
from .candidates import render_candidates_page
from .interviews import render_interviews_page
from .jobs import render_jobs_page  # Add this

__all__ = [
    'render_home_page',
    'render_candidates_page',
    'render_interviews_page',
    'render_jobs_page'  # Add this
]