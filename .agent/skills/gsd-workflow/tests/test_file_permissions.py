"""Tests for file permission errors and edge cases across GSD workflow scripts."""

import pytest
import sys
import os
import stat
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from validate_plan import PlanValidator, main as validate_main
from wave_planner import PlanAnalyzer, main as wave_main
from phase_transition import PhaseManager, main as phase_main
from init_gsd import init_gsd
from plan_merger import PlanMerger


class TestFilePermissionErrors:
    """Test handling of file permission errors."""
    
    def test_read_permission_denied(self, temp_project_dir, sample_plan_file):
        """Test handling of read permission denied on plan file."""
        plan_path = temp_project_dir / "restricted-plan.md"
        plan_path.write_text(sample_plan_file)
        
        # Remove read permission
        plan_path.chmod(0o000)
        
        try:
            validator = PlanValidator(plan_path)
            # Should handle permission error gracefully
            is_valid = validator.validate()
            assert is_valid is False
        finally:
            # Restore permissions for cleanup
            plan_path.chmod(0o644)
    
    def test_write_permission_denied_on_roadmap(self, temp_project_dir):
        """Test handling when ROADMAP.md is read-only."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Test
**Goal**: Test
**Requirements**: R1
**Status**: not-started
"""
        roadmap_path = planning_dir / "ROADMAP.md"
        roadmap_path.write_text(roadmap)
        roadmap_path.chmod(0o444)  # Read-only
        
        (planning_dir / "STATE.md").write_text("# State\n**Phase**: 1\n**Status**: not-started")
        
        try:
            manager = PhaseManager(planning_dir)
            # Try to update status on read-only file
            success = manager.update_phase_status(1, "in-progress")
            # Should fail gracefully
            assert success is False
        finally:
            roadmap_path.chmod(0o644)
    
    def test_write_permission_denied_on_state(self, temp_project_dir):
        """Test handling when STATE.md is read-only."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        roadmap = """# ROADMAP

## Phase 1: Test
**Goal**: Test
**Requirements**: R1
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        
        state_path = planning_dir / "STATE.md"
        state_path.write_text("# State\n**Phase**: 1\n**Status**: not-started")
        state_path.chmod(0o444)  # Read-only
        
        try:
            manager = PhaseManager(planning_dir)
            success = manager.update_state_file(1, "in-progress", "Note")
            # Should fail gracefully
            assert success is False
        finally:
            state_path.chmod(0o644)
    
    def test_directory_not_writable(self, temp_project_dir):
        """Test handling when planning directory is not writable."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Make directory read-only
        planning_dir.chmod(0o555)
        
        try:
            # Try to initialize GSD in read-only directory
            with pytest.raises((PermissionError, OSError)):
                init_gsd(str(temp_project_dir))
        finally:
            planning_dir.chmod(0o755)
    
    def test_create_file_in_nonexistent_directory(self, temp_project_dir):
        """Test handling of file creation in non-existent nested directory."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Create merger and try to work with non-existent subdirectories
        merger = PlanMerger(planning_dir)
        
        # Create a plan file
        (planning_dir / "1-1-PLAN.md").write_text("""<plan phase="1" plan="1">
  <overview><phase_name>Test</phase_name><goal>Test</goal></overview>
  <tasks><task type="auto" priority="1"><name>Task</name><action>Do</action><verify>Check</verify></task></tasks>
</plan>""")
        
        # Should work normally when directory exists
        plan = merger.load_plan("1-1-PLAN.md")
        assert plan["phase"] == "1"


class TestCorruptedFiles:
    """Test handling of corrupted or malformed files."""
    
    def test_binary_content_in_plan(self, temp_project_dir):
        """Test handling of binary content in plan file."""
        plan_path = temp_project_dir / "binary-plan.md"
        # Write binary content
        plan_path.write_bytes(b'\x00\x01\x02\x03\xff\xfe')
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        # Should handle gracefully and report errors
        assert is_valid is False
    
    def test_null_bytes_in_plan(self, temp_project_dir):
        """Test handling of null bytes in plan file."""
        plan_path = temp_project_dir / "null-plan.md"
        plan_path.write_text('<plan phase="1"\x00 plan="1"></plan>')
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        # Null bytes might cause parsing issues
        assert is_valid is False
    
    def test_very_long_line(self, temp_project_dir):
        """Test handling of extremely long lines."""
        plan_path = temp_project_dir / "long-line.md"
        long_content = "x" * 100000  # 100KB line
        plan_path.write_text(f'<plan phase="1" plan="1"><overview>{long_content}</overview></plan>')
        
        validator = PlanValidator(plan_path)
        # Should handle without crashing
        validator.validate()
    
    def test_mixed_line_endings(self, temp_project_dir):
        """Test handling of mixed line endings (CRLF, LF, CR)."""
        plan_path = temp_project_dir / "mixed-endings.md"
        content = '<plan phase="1" plan="1">\r\n<overview>\r<phase_name>Test</phase_name>\n</overview>\r\n</plan>'
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        # Should handle mixed line endings
        # Note: This may pass or fail depending on regex robustness
        # The important thing is it doesn't crash
    
    def test_bom_in_file(self, temp_project_dir):
        """Test handling of UTF-8 BOM in plan file."""
        plan_path = temp_project_dir / "bom-plan.md"
        content = '<plan phase="1" plan="1">\n<overview><phase_name>Test</phase_name></overview>\n</plan>'
        # Write with BOM
        plan_path.write_bytes(b'\xef\xbb\xbf' + content.encode('utf-8'))
        
        validator = PlanValidator(plan_path)
        # Should handle BOM without crashing
        validator.validate()


class TestRaceConditions:
    """Test handling of race conditions and concurrent modifications."""
    
    def test_file_deleted_during_read(self, temp_project_dir, sample_plan_file):
        """Test handling when file is deleted during validation."""
        plan_path = temp_project_dir / "deleted-plan.md"
        plan_path.write_text(sample_plan_file)
        
        validator = PlanValidator(plan_path)
        
        # Delete file before validation
        plan_path.unlink()
        
        is_valid = validator.validate()
        assert is_valid is False
        assert any("File not found" in e for e in validator.errors)
    
    def test_file_modified_during_validation(self, temp_project_dir):
        """Test handling when file is modified during validation."""
        plan_path = temp_project_dir / "modified-plan.md"
        plan_path.write_text('<plan phase="1" plan="1">\n<overview><phase_name>Test</phase_name></overview>\n</plan>')
        
        validator = PlanValidator(plan_path)
        
        # Read content first
        content = plan_path.read_text()
        
        # Modify file
        plan_path.write_text('<plan phase="2" plan="2">\n<overview><phase_name>Modified</phase_name></overview>\n</plan>')
        
        # Continue with validation using old content
        validator._check_xml_structure(content)
        # Should complete without error


class TestPathTraversal:
    """Test prevention of path traversal attacks."""
    
    def test_path_traversal_in_plan_filename(self, temp_project_dir):
        """Test that path traversal sequences are handled."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Create a file outside the planning directory
        outside_file = temp_project_dir / "outside.txt"
        outside_file.write_text("secret")
        
        merger = PlanMerger(planning_dir)
        
        # Try to load file using path traversal
        try:
            plan = merger.load_plan("../outside.txt")
            # If it succeeds, verify it didn't actually read outside
            assert "secret" not in plan["content"]
        except (FileNotFoundError, ValueError):
            # Expected - path traversal should be prevented
            pass
    
    def test_absolute_path_in_plan_filename(self, temp_project_dir):
        """Test handling of absolute paths in plan filename."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        merger = PlanMerger(planning_dir)
        
        # Try to load file using absolute path
        try:
            plan = merger.load_plan("/etc/passwd")
            # If it succeeds, content should not be from /etc/passwd
            assert "root:" not in plan["content"]
        except (FileNotFoundError, PermissionError, ValueError):
            # Expected - ValueError for path traversal protection
            pass


class TestDiskSpaceErrors:
    """Test handling of disk space errors."""
    
    def test_write_large_state_update(self, temp_project_dir):
        """Test handling of very large state updates."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Create initial state
        state = "# State\n**Phase**: 1\n**Status**: not-started\n\n## Session Memory\n\n"
        (planning_dir / "STATE.md").write_text(state)
        
        roadmap = """# ROADMAP

## Phase 1: Test
**Goal**: Test
**Requirements**: R1
**Status**: not-started
"""
        (planning_dir / "ROADMAP.md").write_text(roadmap)
        
        manager = PhaseManager(planning_dir)
        
        # Try to add very large note
        large_note = "x" * 1000000  # 1MB note
        success = manager.update_state_file(1, "in-progress", large_note)
        
        # Should succeed or fail gracefully
        if success:
            updated = (planning_dir / "STATE.md").read_text()
            assert large_note in updated


class TestSymlinks:
    """Test handling of symbolic links."""
    
    def test_symlink_to_plan_file(self, temp_project_dir, sample_plan_file):
        """Test validation of symlink to plan file."""
        plan_path = temp_project_dir / "real-plan.md"
        plan_path.write_text(sample_plan_file)
        
        symlink_path = temp_project_dir / "link-plan.md"
        symlink_path.symlink_to(plan_path)
        
        validator = PlanValidator(symlink_path)
        is_valid = validator.validate()
        
        # Should follow symlink and validate
        assert is_valid is True
    
    def test_symlink_to_directory(self, temp_project_dir):
        """Test wave planner with symlinked planning directory."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Create a plan
        (planning_dir / "1-1-PLAN.md").write_text("""<plan phase="1" plan="1">
  <overview><phase_name>Test</phase_name><goal>Test</goal></overview>
  <tasks><task type="auto" priority="1"><name>Task</name><action>Do</action><verify>Check</verify></task></tasks>
</plan>""")
        
        # Create symlink to planning directory
        link_dir = temp_project_dir / ".planning-link"
        link_dir.symlink_to(planning_dir)
        
        analyzer = PlanAnalyzer(link_dir)
        analyzer.load_plans(1)
        
        assert "1-1" in analyzer.plans
    
    def test_broken_symlink(self, temp_project_dir):
        """Test handling of broken symlink."""
        symlink_path = temp_project_dir / "broken-link.md"
        symlink_path.symlink_to(temp_project_dir / "nonexistent.md")
        
        validator = PlanValidator(symlink_path)
        is_valid = validator.validate()
        
        assert is_valid is False


class TestCLIErrorHandling:
    """Test CLI error handling across scripts."""
    
    def test_validate_main_nonexistent_dir(self, temp_project_dir):
        """Test validate_plan main with non-existent directory."""
        nonexistent = temp_project_dir / "does-not-exist"
        
        with patch('sys.argv', ['validate_plan', '--dir', str(nonexistent), '--all']):
            result = validate_main()
            assert result == 1
    
    def test_wave_main_nonexistent_dir(self, temp_project_dir):
        """Test wave_planner main with non-existent directory."""
        nonexistent = temp_project_dir / "does-not-exist"
        
        with patch('sys.argv', ['wave_planner', '1', '--dir', str(nonexistent)]):
            result = wave_main()
            assert result == 1
    
    def test_phase_main_nonexistent_dir(self, temp_project_dir):
        """Test phase_transition main with non-existent directory."""
        nonexistent = temp_project_dir / "does-not-exist"
        
        with patch('sys.argv', ['phase_transition', 'status', '--dir', str(nonexistent)]):
            result = phase_main()
            assert result == 1
    
    def test_invalid_phase_number(self, temp_project_dir):
        """Test handling of invalid phase number."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        with patch('sys.argv', ['wave_planner', 'invalid', '--dir', str(temp_project_dir)]):
            # Should raise SystemExit due to argparse type validation
            with pytest.raises(SystemExit):
                wave_main()


class TestConcurrentAccess:
    """Test handling of concurrent access scenarios."""
    
    def test_multiple_validators_same_file(self, temp_project_dir, sample_plan_file):
        """Test multiple validators accessing the same file."""
        plan_path = temp_project_dir / "shared-plan.md"
        plan_path.write_text(sample_plan_file)
        
        validator1 = PlanValidator(plan_path)
        validator2 = PlanValidator(plan_path)
        
        # Both should be able to validate
        result1 = validator1.validate()
        result2 = validator2.validate()
        
        assert result1 == result2 == True
    
    def test_analyzer_while_file_being_written(self, temp_project_dir):
        """Test analyzer reading while file is being modified."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        plan_path = planning_dir / "1-1-PLAN.md"
        
        # Write initial content
        plan_path.write_text("<plan phase=\"1\" plan=\"1\">\n<overview><phase_name>Initial</phase_name></overview>\n</plan>")
        
        analyzer = PlanAnalyzer(planning_dir)
        
        # Modify file after analyzer is created but before loading
        plan_path.write_text("""<plan phase="1" plan="1">
  <overview><phase_name>Modified</phase_name><goal>Modified</goal></overview>
  <dependencies></dependencies>
  <tasks><task type="auto" priority="1"><name>Task</name><action>Do</action><verify>Check</verify></task></tasks>
</plan>""")
        
        # Load plans - should read current state
        analyzer.load_plans(1)
        
        # Should have loaded the modified content
        assert "1-1" in analyzer.plans


class TestUnicodeAndEncoding:
    """Test handling of various encodings and unicode edge cases."""
    
    def test_utf16_encoded_file(self, temp_project_dir):
        """Test handling of UTF-16 encoded file."""
        plan_path = temp_project_dir / "utf16-plan.md"
        content = '<plan phase="1" plan="1">\n<overview><phase_name>Test</phase_name></overview>\n</plan>'
        plan_path.write_bytes(content.encode('utf-16'))
        
        validator = PlanValidator(plan_path)
        # Should handle or fail gracefully
        try:
            validator.validate()
        except UnicodeError:
            pass  # Expected if UTF-16 not handled
    
    def test_latin1_encoded_file(self, temp_project_dir):
        """Test handling of Latin-1 encoded file with special chars."""
        plan_path = temp_project_dir / "latin1-plan.md"
        # Content with Latin-1 specific characters
        content = '<plan phase="1" plan="1">\n<overview><phase_name>Café résumé</phase_name></overview>\n</plan>'
        plan_path.write_bytes(content.encode('latin-1'))
        
        validator = PlanValidator(plan_path)
        # Should handle or fail gracefully
        validator.validate()
