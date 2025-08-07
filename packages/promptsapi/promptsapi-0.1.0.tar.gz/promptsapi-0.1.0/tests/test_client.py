# tests/test_client.py

import pytest
from promptsapi import generate_prompt

def test_generate_prompt_exists():
    """
    Test that the generate_prompt function can be imported and exists.
    """
    assert callable(generate_prompt)

# You can add more complex tests here once you're ready.
# For example, to check the function's behavior with a mock API response.
