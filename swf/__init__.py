"""swf — shared utilities for the SpaceX / Social Wealth Fund analysis pipeline.

Keeps three things in one place so nothing drifts:
  - paths   : every directory the pipeline reads/writes
  - facts   : the single-source-of-truth loader for data/facts/ipo_facts.yaml
  - theme   : the Burnside-Brutalist Plotly theme + write_html() wrapper matching the site
"""
from . import paths, facts, theme  # noqa: F401
