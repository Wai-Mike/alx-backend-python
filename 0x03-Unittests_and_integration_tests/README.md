# Unit Tests and Integration Tests

This directory contains unit tests and integration tests for the utils and client modules.

## Files

- `utils.py`: Utility functions including `access_nested_map`, `get_json`, and `memoize`
- `client.py`: GitHub organization client implementation
- `test_utils.py`: Unit tests for utility functions
- `test_client.py`: Unit and integration tests for the GitHub client
- `fixtures.py`: Test fixtures for integration tests

## Running Tests

To run the tests, use:

```bash
python -m unittest discover -s . -p "test_*.py"
```

Or run individual test files:

```bash
python -m unittest test_utils
python -m unittest test_client
```

