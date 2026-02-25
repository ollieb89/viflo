# GSD Workflow Tests

Comprehensive test suite for the GSD workflow scripts.

## Test Coverage

| Test File                  | Coverage Area                                        | Test Count |
| -------------------------- | ---------------------------------------------------- | ---------- |
| `test_validate_plan.py`    | XML parsing edge cases, task validation, size limits | 20+ tests  |
| `test_wave_planner.py`     | Circular dependency detection, wave calculation      | 20+ tests  |
| `test_phase_transition.py` | Phase status regex matching, lifecycle management    | 25+ tests  |
| `test_file_permissions.py` | Permission errors, corrupted files, race conditions  | 25+ tests  |

## Running Tests

### Run all tests:

```bash
cd .agent/skills/gsd-workflow/tests
python3 run_tests.py
```

### Run with coverage:

```bash
python3 run_tests.py --cov
```

### Run specific test file:

```bash
python3 run_tests.py test_validate_plan.py
```

### Run with pytest directly:

```bash
pytest -v
pytest test_validate_plan.py -v
pytest -k "test_circular" -v
```

## Test Categories

### XML Parsing Edge Cases (test_validate_plan.py)

- Valid plan structure validation
- Malformed/unclosed tags
- Missing root elements
- Special characters and entities
- Unicode content
- Empty files
- Multiple validation errors

### Circular Dependency Detection (test_wave_planner.py)

- Simple A → B → A cycles
- Self-referential plans
- Triangle cycles (A → B → C → A)
- Multiple independent cycles
- Diamond dependency patterns
- Wave calculation with cycles

### Phase Status Regex (test_phase_transition.py)

- Standard status format parsing
- Whitespace handling
- Multiline phase content
- Special characters in phase names
- Status updates and validation
- Session memory management

### File Permission Errors (test_file_permissions.py)

- Read permission denied
- Write permission denied
- Binary/corrupted files
- Race conditions
- Path traversal attempts
- Symlink handling
- Disk space scenarios

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `temp_project_dir` - Temporary project directory
- `initialized_gsd_project` - Pre-initialized GSD structure
- `sample_plan_file` - Valid plan XML content
- `malformed_plan_*` - Various malformed plan examples
- `plan_with_cycle_*` - Plans creating circular dependencies

## Adding New Tests

1. Create test functions in appropriate test file
2. Use existing fixtures from `conftest.py`
3. Follow naming convention: `test_<description>`
4. Group related tests in classes
5. Run tests before committing changes

## Bug Fixes Tested

This test suite validates fixes for:

1. **Split limit bug** in `phase_transition.py` - Session memory insertion
2. **Missing return** in `validate_plan.py` - All plans validation path
3. **Edge cases** in XML parsing
4. **Permission handling** across all scripts
