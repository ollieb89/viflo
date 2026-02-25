"""Tests for phase_transition.py - Phase status regex matching and lifecycle management."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from phase_transition import PhaseManager, print_status, main


class TestPhaseStatusRegexMatching:
    """Test regex patterns for parsing phase status from ROADMAP.md."""
    
    def test_standard_status_format(self, temp_project_dir):
        """Test parsing standard status format."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Test Phase
**Goal**: Test
**Requirements**: R1
**Status**: in-progress

## Phase 2: Next Phase
**Goal**: Next
**Requirements**: R2
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: in-progress")
        
        manager = PhaseManager(planning_dir)
        
        assert manager.get_phase_status(1) == "in-progress"
        assert manager.get_phase_status(2) == "not-started"
    
    def test_status_with_extra_whitespace(self, temp_project_dir):
        """Test parsing status with varying whitespace."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Test Phase
**Goal**: Test
**Requirements**: R1
**Status**:   complete   

## Phase 2: Test Phase 2
**Goal**: Test
**Requirements**: R2
**Status**:not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: complete")
        
        manager = PhaseManager(planning_dir)
        
        # Should handle extra whitespace
        assert manager.get_phase_status(1) == "complete"
        assert manager.get_phase_status(2) == "not-started"
    
    def test_multiline_phase_content(self, temp_project_dir):
        """Test parsing phase with multiline content between header and status."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Complex Phase
**Goal**: This is a multi-line
goal description that spans
multiple lines
**Requirements**: 
- R1
- R2
**Status**: planning

## Phase 2: Another Phase
**Goal**: Simple
**Requirements**: R3
**Status**: complete
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: planning")
        
        manager = PhaseManager(planning_dir)
        
        assert manager.get_phase_status(1) == "planning"
        assert manager.get_phase_status(2) == "complete"
    
    def test_unknown_phase(self, temp_project_dir):
        """Test handling of non-existent phase."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Only Phase
**Goal**: Test
**Requirements**: R1
**Status**: complete
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: complete")
        
        manager = PhaseManager(planning_dir)
        
        assert manager.get_phase_status(99) == "unknown"
    
    def test_phase_with_colon_in_name(self, temp_project_dir):
        """Test parsing phase with colon in the name."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Auth: Login and Signup
**Goal**: Test
**Requirements**: R1
**Status**: in-progress
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: in-progress")
        
        manager = PhaseManager(planning_dir)
        
        # Should handle colon in phase name
        assert manager.get_phase_status(1) == "in-progress"
    
    def test_phase_with_special_chars_in_content(self, temp_project_dir):
        """Test parsing phase with special regex characters in content."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Special [Chars]
**Goal**: Handle **bold** and *italic* text
**Requirements**: R1.test, R2[feature]
**Status**: executing

## Phase 2: Another
**Goal**: Use $variables and (parentheses)
**Requirements**: R3
**Status**: verifying
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: executing")
        
        manager = PhaseManager(planning_dir)
        
        assert manager.get_phase_status(1) == "executing"
        assert manager.get_phase_status(2) == "verifying"
    
    def test_empty_roadmap(self, temp_project_dir):
        """Test handling of empty roadmap file."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        (planning_dir / "ROADMAP.md").write_text("")
        (planning_dir / "STATE.md").write_text("# State")
        
        manager = PhaseManager(planning_dir)
        
        assert manager.get_phase_status(1) == "unknown"
        assert manager.get_current_phase() is None
    
    def test_missing_roadmap(self, temp_project_dir):
        """Test handling when ROADMAP.md doesn't exist."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        (planning_dir / "STATE.md").write_text("# State")
        
        manager = PhaseManager(planning_dir)
        
        assert manager.get_phase_status(1) == "unknown"
        assert manager.get_current_phase() is None


class TestPhaseStatusUpdate:
    """Test updating phase status in ROADMAP.md."""
    
    def test_update_status_success(self, temp_project_dir):
        """Test successful status update."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Test Phase
**Goal**: Test
**Requirements**: R1
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: not-started")
        
        manager = PhaseManager(planning_dir)
        success = manager.update_phase_status(1, "in-progress")
        
        assert success is True
        
        # Verify file was updated
        updated = (planning_dir / "ROADMAP.md").read_text()
        assert "**Status**: in-progress" in updated
    
    def test_update_invalid_status(self, temp_project_dir):
        """Test rejection of invalid status value."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Test Phase
**Goal**: Test
**Requirements**: R1
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: not-started")
        
        manager = PhaseManager(planning_dir)
        success = manager.update_phase_status(1, "invalid-status")
        
        assert success is False
    
    def test_update_nonexistent_phase(self, temp_project_dir):
        """Test updating status of non-existent phase."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Test Phase
**Goal**: Test
**Requirements**: R1
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: not-started")
        
        manager = PhaseManager(planning_dir)
        success = manager.update_phase_status(99, "in-progress")
        
        assert success is False
    
    def test_update_all_valid_states(self, temp_project_dir):
        """Test updating through all valid state transitions."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Test Phase
**Goal**: Test
**Requirements**: R1
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: not-started")
        
        manager = PhaseManager(planning_dir)
        valid_states = [
            "not-started",
            "discussing",
            "planning",
            "ready-to-execute",
            "executing",
            "verifying",
            "complete"
        ]
        
        for state in valid_states:
            success = manager.update_phase_status(1, state)
            assert success is True, f"Failed to set state: {state}"
            
            updated = (planning_dir / "ROADMAP.md").read_text()
            assert f"**Status**: {state}" in updated


class TestStateFileUpdate:
    """Test updating STATE.md with current phase info."""
    
    def test_update_state_file(self, temp_project_dir):
        """Test successful STATE.md update."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        state = """# Project State

**Phase**: 0
**Status**: unknown

## Blockers

- [ ] None

## Session Memory

"""
        (planning_dir / "STATE.md").write_text(state)
        (planning_dir / "ROADMAP.md").write_text("# ROADMAP\n\n## Phase 1: Test\n**Goal**: Test\n**Status**: in-progress")
        
        manager = PhaseManager(planning_dir)
        success = manager.update_state_file(1, "in-progress", "Started phase 1")
        
        assert success is True
        
        updated = (planning_dir / "STATE.md").read_text()
        assert "**Phase**: 1" in updated
        assert "**Status**: in-progress" in updated
        assert "Started phase 1" in updated
    
    def test_session_memory_insertion(self, temp_project_dir):
        """Test that session entries are inserted in Session Memory section."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        state = """# Project State

**Phase**: 1
**Status**: not-started

## Blockers

## Session Memory

### 2024-01-01 10:00
**Phase 0**: complete

## Decisions

"""
        (planning_dir / "STATE.md").write_text(state)
        (planning_dir / "ROADMAP.md").write_text("# ROADMAP\n\n## Phase 1: Test\n**Goal**: Test\n**Status**: in-progress")
        
        manager = PhaseManager(planning_dir)
        manager.update_state_file(1, "in-progress", "Making progress")
        
        updated = (planning_dir / "STATE.md").read_text()
        # Should have inserted after ## Session Memory
        parts = updated.split("## Session Memory")
        assert len(parts) == 2
        # New entry should be in the first part after the header
        assert "Making progress" in parts[1]
    
    def test_update_state_file_multiple_sessions(self, temp_project_dir):
        """Test handling multiple session entries."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        state = """# Project State

**Phase**: 1
**Status**: discussing

## Session Memory

### 2024-01-01 10:00
**Phase 1**: discussing
Started discussion

"""
        (planning_dir / "STATE.md").write_text(state)
        (planning_dir / "ROADMAP.md").write_text("# ROADMAP\n\n## Phase 1: Test\n**Goal**: Test\n**Status**: planning")
        
        manager = PhaseManager(planning_dir)
        manager.update_state_file(1, "planning", "Started planning")
        
        updated = (planning_dir / "STATE.md").read_text()
        # Should contain both entries
        assert "discussing" in updated
        assert "planning" in updated


class TestPhaseCompletion:
    """Test phase completion validation."""
    
    def test_check_phase_completion_all_complete(self, temp_project_dir):
        """Test completion check when all plans have summaries."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Create plan and summary files
        (planning_dir / "1-1-PLAN.md").write_text("<plan></plan>")
        (planning_dir / "1-1-SUMMARY.md").write_text("# Summary")
        (planning_dir / "1-2-PLAN.md").write_text("<plan></plan>")
        (planning_dir / "1-2-SUMMARY.md").write_text("# Summary")
        
        (planning_dir / "ROADMAP.md").write_text("# ROADMAP\n\n## Phase 1: Test\n**Goal**: Test\n**Status**: executing")
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: executing")
        
        manager = PhaseManager(planning_dir)
        result = manager.check_phase_completion(1)
        
        assert result["all_complete"] is True
        assert result["plans_total"] == 2
        assert result["plans_completed"] == 2
        assert len(result["missing_summaries"]) == 0
    
    def test_check_phase_completion_partial(self, temp_project_dir):
        """Test completion check when some plans lack summaries."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        (planning_dir / "1-1-PLAN.md").write_text("<plan></plan>")
        (planning_dir / "1-1-SUMMARY.md").write_text("# Summary")
        (planning_dir / "1-2-PLAN.md").write_text("<plan></plan>")
        # No summary for 1-2
        
        (planning_dir / "ROADMAP.md").write_text("# ROADMAP\n\n## Phase 1: Test\n**Goal**: Test\n**Status**: executing")
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: executing")
        
        manager = PhaseManager(planning_dir)
        result = manager.check_phase_completion(1)
        
        assert result["all_complete"] is False
        assert result["plans_total"] == 2
        assert result["plans_completed"] == 1
        assert "1-2" in result["missing_summaries"]
    
    def test_check_phase_completion_no_plans(self, temp_project_dir):
        """Test completion check when no plans exist."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        (planning_dir / "ROADMAP.md").write_text("# ROADMAP\n\n## Phase 1: Test\n**Goal**: Test\n**Status**: executing")
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: executing")
        
        manager = PhaseManager(planning_dir)
        result = manager.check_phase_completion(1)
        
        # No plans means not complete
        assert result["all_complete"] is False
        assert result["plans_total"] == 0


class TestPhaseStart:
    """Test starting a new phase."""
    
    def test_start_phase_without_previous_complete(self, temp_project_dir):
        """Test starting phase when previous is not complete."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: First
**Goal**: First
**Requirements**: R1
**Status**: in-progress

## Phase 2: Second
**Goal**: Second
**Requirements**: R2
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: in-progress")
        
        manager = PhaseManager(planning_dir)
        
        with patch('builtins.input', return_value='n'):
            success = manager.start_phase(2)
        
        assert success is False
    
    def test_start_phase_first_phase(self, temp_project_dir):
        """Test starting phase 1 (no previous phase check needed)."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: First
**Goal**: First
**Requirements**: R1
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 0\n**Status**: unknown")
        
        manager = PhaseManager(planning_dir)
        success = manager.start_phase(1)
        
        assert success is True
        assert manager.get_phase_status(1) == "discussing"


class TestCLI:
    """Test command-line interface."""
    
    def test_main_status(self, initialized_gsd_project):
        """Test status command."""
        with patch('sys.argv', ['phase_transition', 'status', '--dir', str(initialized_gsd_project)]):
            result = main()
            assert result == 0
    
    def test_main_start_phase(self, initialized_gsd_project):
        """Test start command."""
        with patch('sys.argv', ['phase_transition', 'start', '1', '--dir', str(initialized_gsd_project)]):
            result = main()
            assert result == 0
    
    def test_main_complete_phase_not_ready(self, initialized_gsd_project):
        """Test complete command when phase not ready."""
        with patch('sys.argv', ['phase_transition', 'complete', '1', '--dir', str(initialized_gsd_project)]):
            result = main()
            assert result == 1  # Should fail - no plans exist
    
    def test_main_set_status(self, initialized_gsd_project):
        """Test set-status command."""
        with patch('sys.argv', ['phase_transition', 'set-status', '1', 'planning', '--dir', str(initialized_gsd_project)]):
            result = main()
            assert result == 0
    
    def test_main_check_all_phases(self, initialized_gsd_project):
        """Test check command for all phases."""
        with patch('sys.argv', ['phase_transition', 'check', '--dir', str(initialized_gsd_project)]):
            result = main()
            assert result == 0
    
    def test_main_no_planning_dir(self, temp_project_dir):
        """Test main when .planning doesn't exist."""
        with patch('sys.argv', ['phase_transition', 'status', '--dir', str(temp_project_dir)]):
            result = main()
            assert result == 1
    
    def test_main_missing_phase_argument(self, initialized_gsd_project):
        """Test error when phase argument missing."""
        with patch('sys.argv', ['phase_transition', 'start', '--dir', str(initialized_gsd_project)]):
            result = main()
            assert result == 1
    
    def test_main_missing_status_argument(self, initialized_gsd_project):
        """Test error when status value missing for set-status."""
        with patch('sys.argv', ['phase_transition', 'set-status', '1', '--dir', str(initialized_gsd_project)]):
            result = main()
            assert result == 1
