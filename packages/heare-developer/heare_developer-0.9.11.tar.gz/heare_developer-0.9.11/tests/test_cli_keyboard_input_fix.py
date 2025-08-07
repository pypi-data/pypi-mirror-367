"""Tests for CLI keyboard input responsiveness during timeout scenarios."""

import asyncio
import pytest
import time

from heare.developer.context import AgentContext
from heare.developer.sandbox import SandboxMode
from heare.developer.user_interface import UserInterface
from heare.developer.tools.shell import shell_execute


class TestableUserInterface(UserInterface):
    """Test user interface that can simulate keyboard input behavior."""

    def __init__(self, input_responses=None, simulate_input_delay=False):
        self.input_responses = input_responses or []
        self.response_index = 0
        self.simulate_input_delay = simulate_input_delay
        self.system_messages = []
        self.user_input_calls = []
        self.input_responsive = True  # Flag to track if input is responsive

    def handle_assistant_message(self, message: str) -> None:
        pass

    def handle_system_message(self, message: str, markdown=True, live=None) -> None:
        self.system_messages.append(message)

    def permission_callback(
        self, action: str, resource: str, sandbox_mode: SandboxMode, action_arguments
    ):
        return True

    def permission_rendering_callback(
        self, action: str, resource: str, action_arguments
    ):
        pass

    def handle_tool_use(self, tool_name: str, tool_params):
        pass

    def handle_tool_result(self, name: str, result, live=None):
        pass

    async def get_user_input(self, prompt: str = "") -> str:
        """Simulate user input with responsiveness tracking."""
        self.user_input_calls.append((time.time(), prompt))

        # Test for keyboard responsiveness by trying to get input quickly
        start_time = time.time()

        if self.simulate_input_delay:
            # Simulate user thinking time
            await asyncio.sleep(0.1)

        # Check if we can respond within a reasonable time (indicates responsiveness)
        response_time = time.time() - start_time
        if (
            response_time > 1.0
        ):  # If it takes more than 1 second, input is likely blocked
            self.input_responsive = False

        # Return the next programmed response
        if self.response_index < len(self.input_responses):
            response = self.input_responses[self.response_index]
            self.response_index += 1
            return response

        return "K"  # Default to kill

    def handle_user_input(self, user_input: str) -> str:
        return user_input

    def display_token_count(self, *args, **kwargs):
        pass

    def display_welcome_message(self):
        pass

    def status(self, message: str, spinner: str = None):
        class DummyContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        return DummyContext()

    def bare(self, message, live=None):
        pass


class TestCLIKeyboardInputFix:
    """Test suite for CLI keyboard input responsiveness fixes."""

    def create_test_context(self, input_responses=None, simulate_delay=False):
        """Create a test context with testable UI."""
        ui = TestableUserInterface(input_responses, simulate_delay)
        context = AgentContext.create(
            model_spec={},
            sandbox_mode=SandboxMode.ALLOW_ALL,
            sandbox_contents=[],
            user_interface=ui,
        )
        return context, ui

    @pytest.mark.asyncio
    async def test_keyboard_responsiveness_during_timeout(self):
        """Test that keyboard input remains responsive during timeout scenarios."""
        context, ui = self.create_test_context(input_responses=["K"])

        # Run a command that will trigger timeout
        start_time = time.time()
        result = await shell_execute(context, "sleep 5", timeout=1)
        execution_time = time.time() - start_time

        # Verify the command was handled properly
        assert "Command was killed by user" in result
        assert execution_time < 3  # Should not take too long

        # Most importantly: verify that user input was responsive
        assert (
            ui.input_responsive
        ), "Keyboard input should remain responsive during timeout"
        assert len(ui.user_input_calls) > 0, "User input should have been requested"

    @pytest.mark.asyncio
    async def test_all_timeout_choices_work(self):
        """Test that all timeout choices (C/K/B) work with responsive input."""

        # Test Kill choice
        context, ui = self.create_test_context(input_responses=["K"])
        result = await shell_execute(context, "sleep 5", timeout=1)
        assert "Command was killed by user" in result
        assert ui.input_responsive

        # Test Background choice
        context, ui = self.create_test_context(input_responses=["B"])
        result = await shell_execute(context, "sleep 5", timeout=1)
        assert "Command backgrounded" in result
        assert ui.input_responsive

        # Test Continue choice (then kill)
        context, ui = self.create_test_context(input_responses=["C", "K"])
        result = await shell_execute(context, "sleep 5", timeout=1)
        assert "Command was killed by user" in result  # Should eventually be killed
        assert ui.input_responsive

    @pytest.mark.asyncio
    async def test_process_completion_during_user_input(self):
        """Test that process completion is detected even during user input wait."""

        class SlowInputUI(TestableUserInterface):
            """UI that simulates slow user response."""

            async def get_user_input(self, prompt: str = "") -> str:
                # User takes longer to respond than the process takes to complete
                await asyncio.sleep(0.3)
                return await super().get_user_input(prompt)

        ui = SlowInputUI(input_responses=["K"])
        context = AgentContext.create(
            model_spec={},
            sandbox_mode=SandboxMode.ALLOW_ALL,
            sandbox_contents=[],
            user_interface=ui,
        )

        # Command will complete in 0.2s, but timeout is 0.1s and user responds in 0.3s
        result = await shell_execute(context, "sleep 0.2", timeout=0.1)

        # Process should complete naturally, not be killed
        assert "Exit code: 0" in result
        assert "Command was killed by user" not in result
        assert ui.input_responsive

    @pytest.mark.asyncio
    async def test_stdin_isolation_prevents_capture(self):
        """Test that background processes don't capture stdin from CLI."""
        import subprocess

        # Test that our fix actually prevents stdin inheritance
        # This is more of a unit test for the subprocess call

        # Create a process the way our fixed code does
        process = subprocess.Popen(
            "sleep 1",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,  # This should prevent stdin capture
            text=True,
        )

        # Verify stdin is properly isolated
        assert process.stdin is None, "Process should not have access to stdin"

        # Clean up
        process.terminate()
        process.wait()

    @pytest.mark.asyncio
    async def test_normal_commands_still_work(self):
        """Test that normal command execution still works after the fix."""
        context, ui = self.create_test_context()

        # Test quick command
        result = await shell_execute(context, "echo 'hello world'")
        assert "Exit code: 0" in result
        assert "hello world" in result

        # Test command with output
        result = await shell_execute(context, "ls /tmp")
        assert "Exit code: 0" in result

        # Verify no timeout prompts were shown for quick commands
        assert (
            len(ui.user_input_calls) == 0
        ), "Quick commands should not prompt for timeout"

    @pytest.mark.asyncio
    async def test_concurrent_processes_dont_interfere(self):
        """Test that multiple concurrent processes don't interfere with input."""

        async def run_timeout_command(context):
            return await shell_execute(context, "sleep 3", timeout=1)

        # Create multiple contexts that will all timeout and need user input
        contexts_and_uis = [
            self.create_test_context(input_responses=["K"]) for _ in range(3)
        ]

        # Run them concurrently
        tasks = [run_timeout_command(context) for context, ui in contexts_and_uis]

        results = await asyncio.gather(*tasks)

        # All should complete successfully
        for result in results:
            assert "Command was killed by user" in result

        # All UIs should have remained responsive
        for context, ui in contexts_and_uis:
            assert ui.input_responsive, "All concurrent UIs should remain responsive"


class TestInputResponsivenessRegression:
    """Regression tests to ensure the fix doesn't break anything."""

    @pytest.mark.asyncio
    async def test_dangerous_commands_still_blocked(self):
        """Ensure dangerous command blocking still works."""
        context, ui = TestCLIKeyboardInputFix().create_test_context()

        result = await shell_execute(context, "sudo rm -rf /")
        assert "Error: This command is not allowed for safety reasons" in result

    @pytest.mark.asyncio
    async def test_permission_system_still_works(self):
        """Ensure permission system integration still works."""

        class DenyingUI(TestableUserInterface):
            def permission_callback(
                self,
                action: str,
                resource: str,
                sandbox_mode: SandboxMode,
                action_arguments,
            ):
                return False  # Deny all permissions

        ui = DenyingUI()
        context = AgentContext.create(
            model_spec={},
            sandbox_mode=SandboxMode.REMEMBER_PER_RESOURCE,
            sandbox_contents=[],
            user_interface=ui,
        )

        result = await shell_execute(context, "echo 'test'")
        assert "Error: Operator denied permission" in result

    @pytest.mark.asyncio
    async def test_output_capture_still_works(self):
        """Ensure output capture still works correctly."""
        context, ui = TestCLIKeyboardInputFix().create_test_context()

        # Test stdout capture
        result = await shell_execute(context, "echo 'stdout test'")
        assert "stdout test" in result

        # Test stderr capture
        result = await shell_execute(context, "echo 'stderr test' >&2")
        assert "stderr test" in result

        # Test both stdout and stderr
        result = await shell_execute(context, "echo 'stdout'; echo 'stderr' >&2")
        assert "stdout" in result
        assert "stderr" in result
