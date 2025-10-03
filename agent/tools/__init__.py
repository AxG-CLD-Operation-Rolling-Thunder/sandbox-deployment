# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tools package for Plan on a Page Agent
"""

from .plan_analyzer import analyze_plan, quick_completeness_check, get_grl_specific_feedback
from .plan_generator import generate_new_plan, get_section_prompts, get_plan_template_blank
from .grl_helper import guide_grl_assignment, suggest_adopt_adapt_invent, get_grl_best_practices, format_grl_table_entry
from .plan_formatter import format_plan_output, validate_format_compliance, extract_plan_data_from_text
from .plan_validator import validate_plan_completeness, quick_validation
from .duplicate_detector import search_similar_plans, check_for_duplicates_simple
from .plan_template_knowledge import get_template, get_section_guidance, get_grl_framework_guide
from .file_upload_supprt import list_artifacts, get_artifact

# Import RAG search functions (will be None if RAG not configured)
try:
    from .plan_rag_search_tool import (
        plan_example_search,
        plan_grl_pattern_search,
        plan_similar_by_type,
        plan_corpus_insights
    )
except ImportError:
    plan_example_search = None
    plan_grl_pattern_search = None
    plan_similar_by_type = None
    plan_corpus_insights = None

__all__ = [
    # Plan Analysis Tools
    'analyze_plan',
    'quick_completeness_check',
    'get_grl_specific_feedback',

    # Plan Generation Tools
    'generate_new_plan',
    'get_section_prompts',
    'get_plan_template_blank',

    # G/R/L Helper Tools
    'guide_grl_assignment',
    'suggest_adopt_adapt_invent',
    'get_grl_best_practices',
    'format_grl_table_entry',

    # Formatting Tools
    'format_plan_output',
    'validate_format_compliance',
    'extract_plan_data_from_text',

    # Validation Tools
    'validate_plan_completeness',
    'quick_validation',

    # Duplicate Detection Tools
    'search_similar_plans',
    'check_for_duplicates_simple',

    # Template & Knowledge Tools
    'get_template',
    'get_section_guidance',
    'get_grl_framework_guide',

    # File Upload Support
    'list_artifacts',
    'get_artifact'
]

# Conditionally add RAG search tools if available
if plan_example_search is not None:
    __all__.extend([
        'plan_example_search',
        'plan_grl_pattern_search',
        'plan_similar_by_type',
        'plan_corpus_insights'
    ])
