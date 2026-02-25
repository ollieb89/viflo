"""Tests for wave_planner.py - Circular dependency detection and wave calculation."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from wave_planner import PlanAnalyzer, main


class TestCircularDependencyDetection:
    """Test detection of circular dependencies between plans."""
    
    def test_simple_cycle_a_to_b_to_a(self, temp_project_dir, plan_with_cycle_1, plan_with_cycle_2):
        """Test detection of simple A -> B -> A cycle."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Create two plans that depend on each other
        (planning_dir / "1-1-PLAN.md").write_text(plan_with_cycle_1)
        (planning_dir / "1-2-PLAN.md").write_text(plan_with_cycle_2)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        cycles = analyzer.detect_cycles()
        
        assert len(cycles) > 0
        # Cycle should contain both plans
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)
        assert "1-1" in cycle_nodes
        assert "1-2" in cycle_nodes
    
    def test_self_referential_cycle(self, temp_project_dir, plan_with_self_cycle):
        """Test detection of plan that depends on itself."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_with_self_cycle)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        cycles = analyzer.detect_cycles()
        
        assert len(cycles) > 0
        assert any("1-1" in cycle for cycle in cycles)
    
    def test_triangle_cycle(self, temp_project_dir):
        """Test detection of A -> B -> C -> A cycle."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Plan A depends on Plan C
        plan_a = """<plan phase="1" plan="1">
  <overview><phase_name>Plan A</phase_name><goal>A</goal></overview>
  <dependencies><complete>Plan 3</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task A</name><action>Do A</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan B depends on Plan A
        plan_b = """<plan phase="1" plan="2">
  <overview><phase_name>Plan B</phase_name><goal>B</goal></overview>
  <dependencies><complete>Plan 1</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task B</name><action>Do B</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan C depends on Plan B
        plan_c = """<plan phase="1" plan="3">
  <overview><phase_name>Plan C</phase_name><goal>C</goal></overview>
  <dependencies><complete>Plan 2</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task C</name><action>Do C</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_a)
        (planning_dir / "1-2-PLAN.md").write_text(plan_b)
        (planning_dir / "1-3-PLAN.md").write_text(plan_c)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        cycles = analyzer.detect_cycles()
        
        assert len(cycles) > 0
        # Should detect the cycle through all three plans
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)
        assert "1-1" in cycle_nodes
        assert "1-2" in cycle_nodes
        assert "1-3" in cycle_nodes
    
    def test_no_cycle_in_dag(self, temp_project_dir):
        """Test that valid DAG (no cycles) is correctly identified."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Plan A - no dependencies
        plan_a = """<plan phase="1" plan="1">
  <overview><phase_name>Plan A</phase_name><goal>A</goal></overview>
  <dependencies></dependencies>
  <tasks><task type="auto" priority="1"><name>Task A</name><action>Do A</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan B depends on A
        plan_b = """<plan phase="1" plan="2">
  <overview><phase_name>Plan B</phase_name><goal>B</goal></overview>
  <dependencies><complete>Plan 1</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task B</name><action>Do B</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan C depends on A and B
        plan_c = """<plan phase="1" plan="3">
  <overview><phase_name>Plan C</phase_name><goal>C</goal></overview>
  <dependencies><complete>Plan 1</complete><complete>Plan 2</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task C</name><action>Do C</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_a)
        (planning_dir / "1-2-PLAN.md").write_text(plan_b)
        (planning_dir / "1-3-PLAN.md").write_text(plan_c)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        cycles = analyzer.detect_cycles()
        
        assert len(cycles) == 0
    
    def test_multiple_independent_cycles(self, temp_project_dir):
        """Test detection of multiple separate cycles."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Cycle 1: A <-> B
        plan_a = """<plan phase="1" plan="1">
  <overview><phase_name>Plan A</phase_name><goal>A</goal></overview>
  <dependencies><complete>Plan 2</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task A</name><action>Do A</action><verify>Check</verify></task></tasks>
</plan>"""
        
        plan_b = """<plan phase="1" plan="2">
  <overview><phase_name>Plan B</phase_name><goal>B</goal></overview>
  <dependencies><complete>Plan 1</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task B</name><action>Do B</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Cycle 2: C <-> D (different phase to test cross-phase handling)
        plan_c = """<plan phase="1" plan="3">
  <overview><phase_name>Plan C</phase_name><goal>C</goal></overview>
  <dependencies><complete>Plan 4</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task C</name><action>Do C</action><verify>Check</verify></task></tasks>
</plan>"""
        
        plan_d = """<plan phase="1" plan="4">
  <overview><phase_name>Plan D</phase_name><goal>D</goal></overview>
  <dependencies><complete>Plan 3</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task D</name><action>Do D</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_a)
        (planning_dir / "1-2-PLAN.md").write_text(plan_b)
        (planning_dir / "1-3-PLAN.md").write_text(plan_c)
        (planning_dir / "1-4-PLAN.md").write_text(plan_d)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        cycles = analyzer.detect_cycles()
        
        # Should detect both cycles
        assert len(cycles) >= 2


class TestWaveCalculation:
    """Test wave execution scheduling."""
    
    def test_independent_plans_same_wave(self, temp_project_dir):
        """Test that independent plans are scheduled in the same wave."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Two independent plans
        plan_a = """<plan phase="1" plan="1">
  <overview><phase_name>Plan A</phase_name><goal>A</goal></overview>
  <dependencies></dependencies>
  <tasks><task type="auto" priority="1"><name>Task A</name><action>Do A</action><verify>Check</verify></task></tasks>
</plan>"""
        
        plan_b = """<plan phase="1" plan="2">
  <overview><phase_name>Plan B</phase_name><goal>B</goal></overview>
  <dependencies></dependencies>
  <tasks><task type="auto" priority="1"><name>Task B</name><action>Do B</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_a)
        (planning_dir / "1-2-PLAN.md").write_text(plan_b)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        waves = analyzer.calculate_waves()
        
        # Both should be in wave 1
        assert len(waves) == 1
        assert "1-1" in waves[0]
        assert "1-2" in waves[0]
    
    def test_sequential_plans_different_waves(self, temp_project_dir):
        """Test that dependent plans are scheduled in sequential waves."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Plan A - no dependencies (wave 1)
        plan_a = """<plan phase="1" plan="1">
  <overview><phase_name>Plan A</phase_name><goal>A</goal></overview>
  <dependencies></dependencies>
  <tasks><task type="auto" priority="1"><name>Task A</name><action>Do A</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan B depends on A (wave 2)
        plan_b = """<plan phase="1" plan="2">
  <overview><phase_name>Plan B</phase_name><goal>B</goal></overview>
  <dependencies><complete>Plan 1</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task B</name><action>Do B</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan C depends on B (wave 3)
        plan_c = """<plan phase="1" plan="3">
  <overview><phase_name>Plan C</phase_name><goal>C</goal></overview>
  <dependencies><complete>Plan 2</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task C</name><action>Do C</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_a)
        (planning_dir / "1-2-PLAN.md").write_text(plan_b)
        (planning_dir / "1-3-PLAN.md").write_text(plan_c)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        waves = analyzer.calculate_waves()
        
        assert len(waves) == 3
        assert "1-1" in waves[0]
        assert "1-2" in waves[1]
        assert "1-3" in waves[2]
    
    def test_diamond_dependency_pattern(self, temp_project_dir):
        """Test wave calculation for diamond pattern: A -> B,C -> D."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Plan A - base (wave 1)
        plan_a = """<plan phase="1" plan="1">
  <overview><phase_name>Plan A</phase_name><goal>A</goal></overview>
  <dependencies></dependencies>
  <tasks><task type="auto" priority="1"><name>Task A</name><action>Do A</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan B depends on A (wave 2)
        plan_b = """<plan phase="1" plan="2">
  <overview><phase_name>Plan B</phase_name><goal>B</goal></overview>
  <dependencies><complete>Plan 1</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task B</name><action>Do B</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan C depends on A (wave 2)
        plan_c = """<plan phase="1" plan="3">
  <overview><phase_name>Plan C</phase_name><goal>C</goal></overview>
  <dependencies><complete>Plan 1</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task C</name><action>Do C</action><verify>Check</verify></task></tasks>
</plan>"""
        
        # Plan D depends on B and C (wave 3)
        plan_d = """<plan phase="1" plan="4">
  <overview><phase_name>Plan D</phase_name><goal>D</goal></overview>
  <dependencies><complete>Plan 2</complete><complete>Plan 3</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task D</name><action>Do D</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_a)
        (planning_dir / "1-2-PLAN.md").write_text(plan_b)
        (planning_dir / "1-3-PLAN.md").write_text(plan_c)
        (planning_dir / "1-4-PLAN.md").write_text(plan_d)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        waves = analyzer.calculate_waves()
        
        assert len(waves) == 3
        assert "1-1" in waves[0]
        assert "1-2" in waves[1]
        assert "1-3" in waves[1]
        assert "1-4" in waves[2]
    
    def test_wave_calculation_with_cycle(self, temp_project_dir, plan_with_cycle_1, plan_with_cycle_2):
        """Test that waves are calculated even with cycles (remaining plans)."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Add an independent plan
        plan_c = """<plan phase="1" plan="3">
  <overview><phase_name>Plan C</phase_name><goal>C</goal></overview>
  <dependencies></dependencies>
  <tasks><task type="auto" priority="1"><name>Task C</name><action>Do C</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_with_cycle_1)
        (planning_dir / "1-2-PLAN.md").write_text(plan_with_cycle_2)
        (planning_dir / "1-3-PLAN.md").write_text(plan_c)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        waves = analyzer.calculate_waves()
        
        # Plan C should be in wave 1 (no dependencies)
        assert "1-3" in waves[0]
        # The cyclic plans should be in a later wave
        assert any("1-1" in wave or "1-2" in wave for wave in waves)


class TestDependencyExtraction:
    """Test extraction of dependencies from plan files."""
    
    def test_cross_phase_dependency(self, temp_project_dir):
        """Test extraction of dependencies across phases."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        # Plan depends on Phase 1 Plan 2
        plan = """<plan phase="2" plan="1">
  <overview><phase_name>Phase 2 Plan</phase_name><goal>Test</goal></overview>
  <dependencies><complete>Phase 1 Plan 2</complete></dependencies>
  <tasks><task type="auto" priority="1"><name>Task</name><action>Do</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "2-1-PLAN.md").write_text(plan)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(2)
        
        assert "1-2" in analyzer.dependencies["2-1"]
    
    def test_multiple_dependencies(self, temp_project_dir):
        """Test extraction of multiple dependencies from one plan."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        plan = """<plan phase="1" plan="3">
  <overview><phase_name>Multi-dep Plan</phase_name><goal>Test</goal></overview>
  <dependencies>
    <complete>Plan 1</complete>
    <complete>Plan 2</complete>
    <complete>Phase 0 Plan 1</complete>
  </dependencies>
  <tasks><task type="auto" priority="1"><name>Task</name><action>Do</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-3-PLAN.md").write_text(plan)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        deps = analyzer.dependencies["1-3"]
        assert "1-1" in deps
        assert "1-2" in deps
        assert "0-1" in deps
    
    def test_no_dependencies(self, temp_project_dir):
        """Test handling of plan with no dependencies."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        plan = """<plan phase="1" plan="1">
  <overview><phase_name>Standalone Plan</phase_name><goal>Test</goal></overview>
  <dependencies></dependencies>
  <tasks><task type="auto" priority="1"><name>Task</name><action>Do</action><verify>Check</verify></task></tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        assert len(analyzer.dependencies["1-1"]) == 0


class TestDurationEstimation:
    """Test task count and duration estimation."""
    
    def test_task_counting(self, temp_project_dir):
        """Test accurate counting of tasks in a plan."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        plan = """<plan phase="1" plan="1">
  <overview><phase_name>Multi-task Plan</phase_name><goal>Test</goal></overview>
  <tasks>
    <task type="auto" priority="1"><name>Task 1</name><action>Do 1</action><verify>Check</verify></task>
    <task type="auto" priority="2"><name>Task 2</name><action>Do 2</action><verify>Check</verify></task>
    <task type="manual" priority="1"><name>Task 3</name><action>Do 3</action><verify>Check</verify></task>
  </tasks>
</plan>"""
        
        (planning_dir / "1-1-PLAN.md").write_text(plan)
        
        analyzer = PlanAnalyzer(planning_dir)
        analyzer.load_plans(1)
        
        assert analyzer.plans["1-1"]["tasks"] == 3
        assert analyzer.estimate_duration("1-1") == 30  # 3 tasks x 10 min


class TestCLI:
    """Test command-line interface."""
    
    def test_main_with_cycle_exits_error(self, temp_project_dir, plan_with_cycle_1, plan_with_cycle_2):
        """Test that main exits with error code when cycles detected."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        (planning_dir / "1-1-PLAN.md").write_text(plan_with_cycle_1)
        (planning_dir / "1-2-PLAN.md").write_text(plan_with_cycle_2)
        
        with patch('sys.argv', ['wave_planner', '1', '--dir', str(temp_project_dir)]):
            result = main()
            assert result == 1
    
    def test_main_no_cycle_exits_success(self, temp_project_dir):
        """Test that main exits with success when no cycles."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        plan = """<plan phase="1" plan="1">
  <overview><phase_name>Standalone</phase_name><goal>Test</goal></overview>
  <tasks><task type="auto" priority="1"><name>Task</name><action>Do</action><verify>Check</verify></task></tasks>
</plan>"""
        (planning_dir / "1-1-PLAN.md").write_text(plan)
        
        with patch('sys.argv', ['wave_planner', '1', '--dir', str(temp_project_dir)]):
            result = main()
            assert result == 0
    
    def test_main_no_plans_found(self, temp_project_dir):
        """Test main when no plans exist for phase."""
        planning_dir = temp_project_dir / ".planning"
        planning_dir.mkdir()
        
        with patch('sys.argv', ['wave_planner', '1', '--dir', str(temp_project_dir)]):
            result = main()
            assert result == 1
    
    def test_main_no_planning_dir(self, temp_project_dir):
        """Test main when .planning directory doesn't exist."""
        with patch('sys.argv', ['wave_planner', '1', '--dir', str(temp_project_dir)]):
            result = main()
            assert result == 1
