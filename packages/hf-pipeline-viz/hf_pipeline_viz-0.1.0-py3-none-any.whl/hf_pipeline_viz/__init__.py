"""
hf_pipeline_viz
~~~~~~~~~~~~
Helper that turns a Hugging Face `pipeline("text-generation")` call into a
token-by-token attention heat-map.  See README for usage.

Vaibhav Gupta 2025
"""

from .main import viz_generate