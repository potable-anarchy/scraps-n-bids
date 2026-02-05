"""
Test to verify PDD workflow completed successfully.

This test detects the bug reported in issue #3 where the PDD workflow
only completed architecture generation but failed to execute prompt
generation and code generation phases.
"""

import os
import json
import pytest
from pathlib import Path


class TestPDDWorkflowCompleteness:
    """
    Test suite to verify the PDD workflow generated all required artifacts.

    The bug (issue #3) manifests as:
    - Architecture files exist (architecture.json, .pddrc, README.md)
    - BUT prompts/ directory does not exist
    - AND index.html (the main application file) does not exist

    This test will FAIL on the current buggy state and PASS once fixed.
    """

    @pytest.fixture
    def repo_root(self):
        """Return the repository root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def architecture_data(self, repo_root):
        """Load and return architecture.json data."""
        arch_file = repo_root / "architecture.json"
        assert arch_file.exists(), "architecture.json should exist"

        with open(arch_file, 'r') as f:
            return json.load(f)

    def test_architecture_files_exist(self, repo_root):
        """
        Verify architecture generation completed (Step 1-7).

        This test verifies the workflow completed the FIRST phase.
        This should PASS even on the buggy code.
        """
        required_arch_files = [
            "architecture.json",
            ".pddrc",
            "README.md",
            "architecture_diagram.html"
        ]

        for filename in required_arch_files:
            file_path = repo_root / filename
            assert file_path.exists(), f"Architecture file {filename} should exist"

    def test_prompts_directory_exists(self, repo_root, architecture_data):
        """
        Verify prompt generation completed (Step 8).

        This test detects the BUG: prompts/ directory should exist but doesn't.
        This test will FAIL on the current buggy code.
        """
        prompts_dir = repo_root / "prompts"

        # BUG: This assertion will FAIL because prompts/ was never created
        assert prompts_dir.exists(), (
            "prompts/ directory should exist after PDD workflow completes. "
            "Bug: Workflow stopped after architecture generation without "
            "generating prompts (Step 8 skipped)."
        )

        assert prompts_dir.is_dir(), "prompts/ should be a directory"

    def test_prompt_files_generated(self, repo_root, architecture_data):
        """
        Verify all module prompts were generated.

        This test verifies that a .prompt file exists for each module
        defined in architecture.json.

        This test will FAIL on the current buggy code.
        """
        prompts_dir = repo_root / "prompts"

        # architecture.json is an array of module objects
        assert isinstance(architecture_data, list), "architecture.json should be a list"
        assert len(architecture_data) > 0, "architecture.json should define modules"

        # Verify prompts/ directory exists
        assert prompts_dir.exists(), (
            f"prompts/ directory should exist with {len(architecture_data)} .prompt files"
        )

        # Verify each module has a corresponding .prompt file
        for module in architecture_data:
            prompt_filename = module.get("filename")
            assert prompt_filename, f"Module should have 'filename' field: {module}"

            prompt_file = prompts_dir / prompt_filename

            # BUG: These assertions will FAIL because no .prompt files exist
            assert prompt_file.exists(), (
                f"Prompt file {prompt_filename} should exist. "
                f"Bug: Prompt generation (Step 8) was skipped."
            )

            # Verify the prompt file is not empty
            assert prompt_file.stat().st_size > 0, (
                f"Prompt file {prompt_filename} should not be empty"
            )

    def test_application_code_generated(self, repo_root):
        """
        Verify application code was generated (Step 9+).

        For this project, the expected output is index.html containing
        the complete Scraps-n-Bids auction application.

        This test will FAIL on the current buggy code.
        """
        index_file = repo_root / "index.html"

        # BUG: This assertion will FAIL because index.html was never generated
        assert index_file.exists(), (
            "index.html should exist after PDD workflow completes. "
            "Bug: Workflow stopped after architecture generation without "
            "executing code generation (pdd sync commands never ran)."
        )

        # Verify the file has content
        assert index_file.stat().st_size > 0, (
            "index.html should not be empty"
        )

        # Verify it contains expected application elements
        content = index_file.read_text()

        # Based on README.md, the app should have these features
        expected_elements = [
            "Scraps-n-Bids",  # Application title
            "auction",         # Auction functionality
            "bid",             # Bidding functionality
        ]

        for element in expected_elements:
            assert element.lower() in content.lower(), (
                f"index.html should contain '{element}' as part of the "
                f"Scraps-n-Bids auction application"
            )

    def test_deployment_readiness(self, repo_root):
        """
        Verify the repository is ready for Vercel deployment.

        This test validates that the deployment configuration is correct
        AND the required files exist to serve content (avoiding 404).

        This test will FAIL on the current buggy code.
        """
        # Verify vercel.json exists and is valid
        vercel_config = repo_root / "vercel.json"
        assert vercel_config.exists(), "vercel.json should exist"

        with open(vercel_config, 'r') as f:
            config = json.load(f)

        # Check output directory configuration
        # Default is "." (root directory) if not specified
        output_dir = config.get("outputDirectory", ".")

        # Verify index.html exists in the output directory
        if output_dir == ".":
            index_path = repo_root / "index.html"
        else:
            index_path = repo_root / output_dir / "index.html"

        # BUG: This assertion will FAIL - no index.html means 404 on deployment
        assert index_path.exists(), (
            f"index.html should exist in output directory '{output_dir}'. "
            f"Bug: Deployment will return 404 because no content was generated."
        )

    def test_workflow_completion_metadata(self, repo_root):
        """
        Verify workflow completion can be determined from artifacts.

        This test checks that we can definitively say whether the
        workflow completed all phases based on file presence.
        """
        # Phase 1: Architecture generation (Steps 1-7)
        phase1_complete = (repo_root / "architecture.json").exists()

        # Phase 2: Prompt generation (Step 8)
        phase2_complete = (repo_root / "prompts").exists()

        # Phase 3: Code generation (Steps 9+)
        phase3_complete = (repo_root / "index.html").exists()

        # Create summary for debugging
        completion_status = {
            "architecture_generation": phase1_complete,
            "prompt_generation": phase2_complete,
            "code_generation": phase3_complete
        }

        # BUG: This will fail because only phase 1 completed
        assert phase1_complete, "Phase 1 (architecture) should be complete"
        assert phase2_complete, (
            f"Phase 2 (prompts) should be complete. Status: {completion_status}. "
            f"Bug: Workflow stopped prematurely after architecture generation."
        )
        assert phase3_complete, (
            f"Phase 3 (code) should be complete. Status: {completion_status}. "
            f"Bug: Code generation never executed."
        )
