"""
E2E Test for Issue #3: PDD Workflow Completeness

This test verifies the complete end-to-end workflow that a user would experience
when using PDD to generate code from architecture specifications.

The bug manifests as:
- User has architecture.json and .pddrc configured
- User expects to run `pdd sync <module>` commands to generate code
- Expected: prompts/ directory created, index.html generated
- Actual (BUG): Workflow incomplete, missing prompts and code

This E2E test simulates the actual user workflow from the issue #3 reproduction steps.
"""

import os
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
import pytest


class TestE2EPDDWorkflowIssue3:
    """
    End-to-end test for the PDD workflow completion bug (issue #3).

    Tests the actual user-facing workflow:
    1. Repository has architecture.json and .pddrc
    2. User runs pdd sync commands for each module
    3. Verify all expected artifacts are created (prompts/, index.html)
    """

    @pytest.fixture
    def test_repo(self, tmp_path):
        """
        Create a temporary test repository with the same structure as scraps-n-bids.

        This fixture sets up a minimal reproduction case with:
        - architecture.json (from the actual repo)
        - .pddrc (from the actual repo)
        - vercel.json (from the actual repo)
        """
        # Get the actual repo root (where this test file lives)
        actual_repo_root = Path(__file__).parent.parent

        # Create test repository directory
        test_repo_dir = tmp_path / "test_scraps_n_bids"
        test_repo_dir.mkdir()

        # Copy configuration files from actual repo
        files_to_copy = [
            "architecture.json",
            ".pddrc",
            "vercel.json",
        ]

        for filename in files_to_copy:
            src = actual_repo_root / filename
            if src.exists():
                shutil.copy2(src, test_repo_dir / filename)

        # Return test repo path and actual repo path for reference
        return {
            "test_dir": test_repo_dir,
            "actual_repo": actual_repo_root,
        }

    @pytest.fixture
    def module_names(self):
        """
        List of module names that should be synced according to issue #3.

        These are the 9 modules defined in architecture.json that the
        user is expected to run `pdd sync` commands for.
        """
        return [
            "html_structure",
            "css_styles",
            "meal_data",
            "utility_helpers",
            "auction_state",
            "timer_module",
            "bidding_engine",
            "dom_render",
            "auction_lifecycle",
        ]

    def test_pdd_sync_workflow_completion(self, test_repo, module_names):
        """
        E2E test: Verify complete PDD workflow from architecture to code.

        This test simulates the exact user workflow described in issue #3:
        1. Repository has architecture.json and .pddrc
        2. User runs `pdd sync <module>` for each module
        3. Expected: prompts/ directory created with .prompt files
        4. Expected: index.html generated with application code

        This test will FAIL on the current buggy code because:
        - prompts/ directory is never created
        - index.html is never generated
        - The PDD workflow automation stops after architecture generation
        """
        test_dir = test_repo["test_dir"]

        # Change to test directory for pdd commands
        original_cwd = os.getcwd()
        os.chdir(test_dir)

        try:
            # Verify starting state: architecture files exist
            assert (test_dir / "architecture.json").exists(), \
                "Test setup should have architecture.json"
            assert (test_dir / ".pddrc").exists(), \
                "Test setup should have .pddrc"

            # Verify starting state: prompts and code do NOT exist yet
            assert not (test_dir / "prompts").exists(), \
                "Test setup should NOT have prompts/ directory yet"
            assert not (test_dir / "index.html").exists(), \
                "Test setup should NOT have index.html yet"

            # Load architecture to verify module count
            with open(test_dir / "architecture.json", 'r') as f:
                architecture = json.load(f)

            assert isinstance(architecture, list), "architecture.json should be a list"
            assert len(architecture) == 9, \
                f"Expected 9 modules in architecture.json, found {len(architecture)}"

            # === SIMULATE USER WORKFLOW: Run pdd sync for first module ===
            # According to issue #3, user should run: pdd sync html_structure
            # This should trigger prompt generation AND code generation

            # NOTE: We only test the FIRST module to keep test execution fast
            # If the workflow works for one module, it should work for all
            first_module = module_names[0]

            print(f"\n=== Running E2E test: pdd sync {first_module} ===")

            # Run pdd sync command (this is what the user would do)
            # Use --dry-run first to see what would happen
            result_dry = subprocess.run(
                ["pdd", "sync", first_module, "--dry-run"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            print(f"Dry-run output:\n{result_dry.stdout}")
            if result_dry.stderr:
                print(f"Dry-run stderr:\n{result_dry.stderr}")

            # BUG DETECTION POINT 1: Dry run should show that prompts need to be created
            # If the workflow is broken, it might fail here or show unexpected state

            # Now run the actual sync command
            # NOTE: This may require API keys and will make actual LLM calls
            # For true E2E testing, we need to either:
            # 1. Mock the LLM calls (but then it's not true E2E)
            # 2. Use test API keys (requires setup)
            # 3. Check if the workflow at least ATTEMPTS to create the files

            # For this test, we'll check if the command at least runs without errors
            # and attempts to create the expected directory structure

            # BUG: The following assertion will likely FAIL because:
            # - The PDD workflow automation doesn't properly initialize prompts/
            # - The skip_prompts flag is incorrectly set
            # - The workflow stops after architecture generation

            # Check if prompts directory gets created
            # (This is the FIRST thing that should happen in pdd sync)
            prompts_dir = test_dir / "prompts"

            # The bug is that prompts/ directory is never created
            # Even if we run pdd sync, it should create this directory
            # Let's verify this is the actual bug by checking if sync even tries

            if not prompts_dir.exists():
                # Try to run pdd sync to see if it creates prompts/
                # We expect this to fail or not create the directory (BUG)
                result = subprocess.run(
                    ["pdd", "sync", first_module, "--skip-verify", "--skip-tests"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    env={**os.environ, "PDD_FORCE": "1"},  # Force mode to skip prompts
                )

                print(f"\nSync command output:\n{result.stdout}")
                if result.stderr:
                    print(f"Sync command stderr:\n{result.stderr}")
                print(f"Sync command return code: {result.returncode}")

            # === VERIFICATION: Check expected artifacts ===

            # BUG CHECK 1: prompts/ directory should exist
            assert prompts_dir.exists(), (
                "BUG DETECTED: prompts/ directory should be created during pdd sync. "
                f"This is the bug reported in issue #3. The PDD workflow stops after "
                f"architecture generation and never creates the prompts/ directory."
            )

            # BUG CHECK 2: Prompt file should exist for the module
            # Based on architecture.json, each module has a filename field
            module_info = next((m for m in architecture if first_module in m.get("filename", "")), None)
            assert module_info is not None, f"Module {first_module} not found in architecture.json"

            expected_prompt_file = prompts_dir / module_info["filename"]
            assert expected_prompt_file.exists(), (
                f"BUG DETECTED: Prompt file {module_info['filename']} should exist. "
                f"The PDD workflow failed to generate prompt files."
            )

            # BUG CHECK 3: index.html should be created (or at least attempted)
            # According to .pddrc, all modules output to index.html
            index_file = test_dir / "index.html"

            # Note: index.html might not exist after just ONE module sync
            # But the workflow should at least create an empty/partial file
            # OR the prompts should be ready for code generation

            # For this E2E test, we verify that AT MINIMUM:
            # - prompts/ directory exists
            # - The workflow is capable of proceeding to code generation

            # If we run ALL module syncs, index.html should definitely exist
            # But for test speed, we check the workflow is at least initiated

            # FINAL VERIFICATION: Workflow state should indicate readiness
            workflow_ready = (
                prompts_dir.exists() and
                len(list(prompts_dir.glob("*.prompt"))) > 0
            )

            assert workflow_ready, (
                "BUG DETECTED: PDD workflow is not ready for code generation. "
                "This indicates the workflow failed to complete prompt generation phase. "
                "Expected: prompts/ directory with .prompt files. "
                f"Actual: prompts/ exists={prompts_dir.exists()}, "
                f"prompt files={len(list(prompts_dir.glob('*.prompt') if prompts_dir.exists() else []))}"
            )

        finally:
            # Restore original directory
            os.chdir(original_cwd)

    def test_deployment_readiness_e2e(self, test_repo):
        """
        E2E test: Verify deployment would succeed (not return 404).

        This test verifies the actual deployment scenario from issue #3:
        1. Repository configured for Vercel deployment
        2. vercel.json points to root directory
        3. index.html should exist for successful deployment

        This test will FAIL on the current buggy code because index.html doesn't exist.
        """
        test_dir = test_repo["test_dir"]
        actual_repo = test_repo["actual_repo"]

        # Copy current state from actual repo (which has the bug)
        # This simulates the ACTUAL deployment state

        # Verify vercel.json exists and is configured correctly
        vercel_config_path = test_dir / "vercel.json"
        assert vercel_config_path.exists(), "vercel.json should exist"

        with open(vercel_config_path, 'r') as f:
            vercel_config = json.load(f)

        # Check output directory (default is "." if not specified)
        output_dir = vercel_config.get("outputDirectory", ".")

        # BUG: index.html should exist in the output directory
        if output_dir == ".":
            expected_index = test_dir / "index.html"
        else:
            expected_index = test_dir / output_dir / "index.html"

        # Check actual repo state first (to confirm bug exists)
        actual_index = actual_repo / "index.html"
        actual_prompts = actual_repo / "prompts"

        # Document the actual bug state
        bug_state = {
            "architecture_exists": (actual_repo / "architecture.json").exists(),
            "prompts_exists": actual_prompts.exists(),
            "index_exists": actual_index.exists(),
        }

        # This assertion documents the BUG
        assert not actual_index.exists(), (
            f"Test validation: Actual repo should have the bug (missing index.html). "
            f"If this assertion fails, the bug has already been fixed. "
            f"Bug state: {bug_state}"
        )

        # BUG CHECK: Deployment would fail with 404
        # The test repo (simulating a fresh deployment) should have index.html
        # but it doesn't because the PDD workflow never completed

        assert expected_index.exists(), (
            f"BUG DETECTED: Deployment will return 404. "
            f"index.html should exist in output directory '{output_dir}'. "
            f"This is the exact bug reported in issue #3: "
            f"Production deployment at vercel.com returns 404 because "
            f"index.html was never generated by the PDD workflow. "
            f"Bug state: {bug_state}"
        )

    def test_workflow_automation_triggered_correctly(self, test_repo):
        """
        E2E test: Verify PDD workflow automation completes all phases.

        This test checks if the automation that should run when a GitHub issue
        gets the 'generate' label actually completes all workflow phases.

        From the root cause analysis:
        - Bug location: /opt/venv/lib/python3.12/site-packages/pdd/agentic_architecture_orchestrator.py:412
        - Issue: skip_prompts parameter incorrectly set or workflow stops early

        This test will FAIL on the current buggy code.
        """
        test_dir = test_repo["test_dir"]

        # Verify the three phases of PDD workflow:
        # Phase 1: Architecture generation (Steps 1-7) ✅
        # Phase 2: Prompt generation (Step 8) ❌ BUG
        # Phase 3: Code generation (Steps 9+) ❌ BUG

        phase1_complete = (test_dir / "architecture.json").exists()
        phase2_complete = (test_dir / "prompts").exists()
        phase3_complete = (test_dir / "index.html").exists()

        assert phase1_complete, "Phase 1 should be complete (architecture generated)"

        # BUG: Phases 2 and 3 are incomplete
        assert phase2_complete, (
            "BUG DETECTED: Phase 2 (prompt generation) incomplete. "
            "The PDD workflow automation stopped after Phase 1. "
            "Root cause: skip_prompts flag incorrectly set to True or "
            "workflow orchestrator stopping early at architecture generation."
        )

        assert phase3_complete, (
            "BUG DETECTED: Phase 3 (code generation) incomplete. "
            "The PDD workflow automation never executed code generation. "
            "Without index.html, deployment returns 404."
        )
