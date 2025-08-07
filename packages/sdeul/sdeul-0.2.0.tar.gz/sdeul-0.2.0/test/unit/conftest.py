"""Pytest configuration file."""

import json

TEST_TEXT = "This is a test input text."
TEST_SCHEMA = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
}
TEST_LLM_OUTPUT_JSON = """{
    "name": "John Doe",
    "age": 30
}"""
TEST_LLM_OUTPUT = json.loads(TEST_LLM_OUTPUT_JSON)
TEST_LLM_OUTPUT_MD = f"""
Here is the output of the LLM:

```json
{TEST_LLM_OUTPUT_JSON}
```
"""

TEST_TEMPERATURE = 0.7
TEST_TOP_P = 0.9
TEST_MAX_TOKENS = 2048
TEST_TIMEOUT = 30
TEST_MAX_RETRIES = 3
