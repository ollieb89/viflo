"""Tests for validate_plan.py - XML parsing edge cases and plan validation."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from validate_plan import PlanValidator, validate_all_plans, main


class TestXMLParsingEdgeCases:
    """Test edge cases in XML plan parsing."""
    
    def test_valid_plan_passes(self, temp_project_dir, sample_plan_file):
        """Test that a valid plan passes all validations."""
        plan_path = temp_project_dir / "valid-plan.md"
        plan_path.write_text(sample_plan_file)
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        assert is_valid is True
        assert len(validator.errors) == 0
    
    def test_malformed_unclosed_tag(self, temp_project_dir, malformed_plan_unclosed_tag):
        """Test detection of unclosed XML tags."""
        plan_path = temp_project_dir / "unclosed.md"
        plan_path.write_text(malformed_plan_unclosed_tag)
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        assert is_valid is False
        assert any("Unbalanced tags" in e for e in validator.errors)
    
    def test_missing_root_element(self, temp_project_dir, malformed_plan_missing_root):
        """Test detection of missing plan root element."""
        plan_path = temp_project_dir / "no-root.md"
        plan_path.write_text(malformed_plan_missing_root)
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        assert is_valid is False
        assert any("Missing or malformed <plan" in e for e in validator.errors)
    
    def test_missing_closing_tag(self, temp_project_dir):
        """Test detection of missing closing </plan> tag."""
        content = '<plan phase="1" plan="1"><overview></overview>'
        plan_path = temp_project_dir / "no-close.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        assert is_valid is False
        assert any("Missing closing </plan>" in e for e in validator.errors)
    
    def test_empty_plan_file(self, temp_project_dir):
        """Test validation of empty plan file."""
        plan_path = temp_project_dir / "empty.md"
        plan_path.write_text("")
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        assert is_valid is False
        # Should have multiple errors for empty file
        assert len(validator.errors) > 0
    
    def test_plan_with_nested_tags(self, temp_project_dir):
        """Test handling of deeply nested XML structures."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Nested Test</phase_name>
    <goal>
      <nested>Deep nesting</nested>
    </goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>Complex task</name>
      <action>
        <step>Step 1</step>
        <step>Step 2</step>
      </action>
      <verify>Done</verify>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "nested.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        # Should pass - we allow content within tags
        assert is_valid is True
    
    def test_special_characters_in_content(self, temp_project_dir):
        """Test handling of special XML characters in content."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Special &amp; Characters</phase_name>
    <goal>Test &lt;script&gt; tags</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>Task with "quotes" and 'apostrophes'</name>
      <action>Use command: git commit -m "message"</action>
      <verify>Check output</verify>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "special.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        # Should handle escaped characters
        assert is_valid is True
    
    def test_unicode_content(self, temp_project_dir):
        """Test handling of unicode characters in plan."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Unicode Test 🚀</phase_name>
    <goal>Test with émojis and ñoño characters</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>Café résumé naïve</name>
      <action>Process 日本語 text</action>
      <verify>✓ Verified</verify>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "unicode.md"
        plan_path.write_text(content, encoding='utf-8')
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        assert is_valid is True
    
    def test_multiple_validation_errors(self, temp_project_dir):
        """Test accumulation of multiple validation errors."""
        content = """<plan phase="bad" plan="worse">
  <overview>
  </overview>
</plan>"""
        plan_path = temp_project_dir / "multiple-errors.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        assert is_valid is False
        # Should collect multiple errors
        assert len(validator.errors) >= 1


class TestTaskValidation:
    """Test task-specific validation rules."""
    
    def test_invalid_task_type(self, temp_project_dir):
        """Test detection of invalid task type."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="invalid" priority="1">
      <name>Bad task</name>
      <action>Do something</action>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "bad-task-type.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        assert any("Invalid type" in e for e in validator.errors)
    
    def test_missing_task_name(self, temp_project_dir):
        """Test detection of missing task name."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <action>No name here</action>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "no-task-name.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        assert any("Missing <name>" in e for e in validator.errors)
    
    def test_missing_task_action(self, temp_project_dir):
        """Test detection of missing task action."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>No action task</name>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "no-action.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        assert any("Missing <action>" in e for e in validator.errors)
    
    def test_empty_action_warning(self, temp_project_dir):
        """Test warning for empty or placeholder action."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>Placeholder task</name>
      <action>TODO:</action>
      <verify>Check</verify>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "placeholder.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        assert any("Action is empty or placeholder" in w for w in validator.warnings)
    
    def test_task_size_limit(self, temp_project_dir):
        """Test warning for oversized tasks."""
        # Create a task with many lines
        long_action = "\n".join([f"    Step {i} of the process" for i in range(60)])
        content = f"""<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>Big task</name>
      <action>
{long_action}
      </action>
      <verify>Check</verify>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "big-task.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        assert any("Task 1 is" in w and "lines" in w for w in validator.warnings)


class TestPlanSizeLimits:
    """Test plan size limit validations."""
    
    def test_oversized_plan_warning(self, temp_project_dir):
        """Test warning for plans exceeding 150 lines."""
        # Create a plan with many lines to exceed 150
        lines = ['<plan phase="1" plan="1">', '  <overview>']
        lines.append('    <phase_name>Big Plan</phase_name>')
        lines.append('    <goal>Many tasks</goal>')
        lines.append('  </overview>')
        lines.append('  <tasks>')
        
        # Add enough tasks to exceed 150 lines
        for i in range(30):
            lines.append(f'    <task type="auto" priority="1">')
            lines.append(f'      <name>Task {i}</name>')
            lines.append(f'      <action>Do something for task {i}</action>')
            lines.append(f'      <verify>Check task {i}</verify>')
            lines.append(f'    </task>')
        
        lines.append('  </tasks>')
        lines.append('</plan>')
        
        plan_path = temp_project_dir / "big-plan.md"
        plan_path.write_text('\n'.join(lines))
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        assert any("Plan is" in w and "lines" in w for w in validator.warnings)


class TestFileOperations:
    """Test file operation edge cases."""
    
    def test_nonexistent_file(self, temp_project_dir):
        """Test validation of non-existent file."""
        plan_path = temp_project_dir / "does-not-exist.md"
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        
        assert is_valid is False
        assert any("File not found" in e for e in validator.errors)
    
    def test_empty_directory_validation(self, initialized_gsd_project):
        """Test validation when no plan files exist."""
        planning_dir = initialized_gsd_project / ".planning"
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            validate_all_plans(planning_dir)
            
            # Should print "No plan files found"
            mock_print.assert_any_call("No plan files found.")


class TestBestPractices:
    """Test best practices warnings."""
    
    def test_missing_verify_warning(self, temp_project_dir):
        """Test warning for missing verify steps."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>No verify task</name>
      <action>Do something</action>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "no-verify.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        assert any("No verification steps" in w for w in validator.warnings)
    
    def test_missing_done_criteria_warning(self, temp_project_dir):
        """Test warning for auto tasks missing done criteria."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>No done task</name>
      <action>Do something</action>
      <verify>Check</verify>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "no-done.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        assert any("Missing <done> criteria" in w for w in validator.warnings)
    
    def test_manual_task_no_done_ok(self, temp_project_dir):
        """Test that manual tasks don't require done criteria."""
        content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="manual" priority="1">
      <name>Manual task</name>
      <action>User does something</action>
      <verify>Check</verify>
    </task>
  </tasks>
</plan>"""
        plan_path = temp_project_dir / "manual-no-done.md"
        plan_path.write_text(content)
        
        validator = PlanValidator(plan_path)
        validator.validate()
        
        # Should NOT warn about missing done for manual tasks
        assert not any("Missing <done>" in w for w in validator.warnings)


class TestCLI:
    """Test command-line interface behavior."""
    
    def test_main_with_nonexistent_planning_dir(self, temp_project_dir):
        """Test main function with non-existent .planning directory."""
        with patch('sys.argv', ['validate_plan', '--dir', str(temp_project_dir)]):
            result = main()
            assert result == 1
    
    def test_main_validate_all(self, initialized_gsd_project):
        """Test --all flag validation."""
        planning_dir = initialized_gsd_project / ".planning"
        
        # Create a valid plan
        plan_content = """<plan phase="1" plan="1">
  <overview>
    <phase_name>Test</phase_name>
    <goal>Test</goal>
  </overview>
  <tasks>
    <task type="auto" priority="1">
      <name>Task</name>
      <action>Do</action>
      <verify>Check</verify>
      <done>Done</done>
    </task>
  </tasks>
</plan>"""
        (planning_dir / "1-1-PLAN.md").write_text(plan_content)
        
        with patch('sys.argv', ['validate_plan', '--dir', str(initialized_gsd_project), '--all']):
            result = main()
            assert result == 0
