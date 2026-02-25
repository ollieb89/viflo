"""Pytest configuration and shared fixtures for GSD workflow tests."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="gsd_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def initialized_gsd_project(temp_project_dir):
    """Create a GSD-initialized project with all artifacts."""
    planning_dir = temp_project_dir / ".planning"
    planning_dir.mkdir()
    
    # Create directory structure
    (planning_dir / "research").mkdir()
    (planning_dir / "todos").mkdir()
    
    # Create STATE.md
    state_content = """# Project State

**Phase**: 1
**Status**: not-started

## Blockers

- [ ] None

## Session Memory

"""
    (planning_dir / "STATE.md").write_text(state_content)
    
    # Create ROADMAP.md
    roadmap_content = """# ROADMAP

## Phase 1: Test Phase
**Goal**: Test phase for unit tests
**Requirements**: TEST-01
**Status**: not-started

## Phase 2: Second Phase
**Goal**: Another test phase
**Requirements**: TEST-02
**Status**: not-started
"""
    (planning_dir / "ROADMAP.md").write_text(roadmap_content)
    
    # Create config.json
    config_content = """{
  "mode": "interactive",
  "depth": "standard",
  "profile": "balanced"
}"""
    (planning_dir / "config.json").write_text(config_content)
    
    return temp_project_dir


@pytest.fixture
def sample_plan_file():
    """Return a sample valid plan file content."""
    return """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test Phase</phase_name>
    <goal>Test goal for validation</goal>
  </overview>
  
  <dependencies>
    <complete>Phase 0: Setup</complete>
  </dependencies>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create test file</name>
      <files>test.txt</files>
      <action>Create a test file</action>
      <verify>File exists</verify>
      <done>Test file created</done>
    </task>
  </tasks>
</plan>
"""


@pytest.fixture
def malformed_plan_unclosed_tag():
    """Return a plan with unclosed tag."""
    return """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test Phase
  </overview>
</plan>
"""


@pytest.fixture
def malformed_plan_missing_root():
    """Return a plan without proper root element."""
    return """<overview>
  <phase_name>Test Phase</phase_name>
</overview>
"""


@pytest.fixture
def plan_with_cycle_1():
    """Return a plan that creates circular dependency A -> B."""
    return """<plan phase="1" plan="1">
  <overview>
    <phase_name>Plan A</phase_name>
    <goal>Depends on B</goal>
  </overview>
  <dependencies>
    <complete>Plan 2</complete>
  </dependencies>
  <tasks>
    <task type="auto" priority="1">
      <name>Task A</name>
      <action>Do A</action>
      <verify>A done</verify>
    </task>
  </tasks>
</plan>
"""


@pytest.fixture
def plan_with_cycle_2():
    """Return a plan that creates circular dependency B -> A."""
    return """<plan phase="1" plan="2">
  <overview>
    <phase_name>Plan B</phase_name>
    <goal>Depends on A</goal>
  </overview>
  <dependencies>
    <complete>Plan 1</complete>
  </dependencies>
  <tasks>
    <task type="auto" priority="1">
      <name>Task B</name>
      <action>Do B</action>
      <verify>B done</verify>
    </task>
  </tasks>
</plan>
"""


@pytest.fixture
def plan_with_self_cycle():
    """Return a plan that depends on itself."""
    return """<plan phase="1" plan="1">
  <overview>
    <phase_name>Self-referential Plan</phase_name>
    <goal>Depends on itself</goal>
  </overview>
  <dependencies>
    <complete>Plan 1</complete>
  </dependencies>
  <tasks>
    <task type="auto" priority="1">
      <name>Task</name>
      <action>Do task</action>
      <verify>Done</verify>
    </task>
  </tasks>
</plan>
"""
