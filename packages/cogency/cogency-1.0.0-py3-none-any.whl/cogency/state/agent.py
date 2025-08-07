"""AgentState - Complete agent state composition."""

from typing import Any, Dict, Optional

from .execution import ExecutionState
from .reasoning import ReasoningContext
from .user import UserProfile


class AgentState:
    """Complete agent state - execution + reasoning + situated memory."""

    def __init__(
        self, query: str, user_id: str = "default", user_profile: Optional[UserProfile] = None
    ):
        self.execution = ExecutionState(query=query, user_id=user_id)
        self.reasoning = ReasoningContext(goal=query)
        self.user = user_profile  # Situated memory

    def get_situated_context(self) -> str:
        """Get user context for prompt injection."""
        if not self.user:
            return ""

        from cogency.memory.compression import compress

        context = compress(self.user)
        return f"USER CONTEXT:\n{context}\n\n" if context else ""

    def update_from_reasoning(self, reasoning_data: Dict[str, Any]) -> None:
        """Update state from LLM reasoning response."""
        # Handle case where LLM returns list instead of dict
        if isinstance(reasoning_data, list):
            if reasoning_data and isinstance(reasoning_data[0], dict):
                reasoning_data = reasoning_data[0]
            else:
                # Fallback: skip update if list doesn't contain valid dict
                return

        # Record thinking
        thinking = reasoning_data.get("thinking", "")
        tool_calls = reasoning_data.get("tool_calls", [])

        if thinking:
            self.reasoning.record_thinking(thinking, tool_calls)

        # Set tool calls for execution
        if tool_calls:
            self.execution.set_tool_calls(tool_calls)

        # Update reasoning context
        context_updates = reasoning_data.get("context_updates", {})
        if context_updates:
            if "goal" in context_updates:
                self.reasoning.goal = context_updates["goal"]
            if "strategy" in context_updates:
                self.reasoning.strategy = context_updates["strategy"]
            if "insights" in context_updates and isinstance(context_updates["insights"], list):
                for insight in context_updates["insights"]:
                    self.reasoning.add_insight(insight)

        # Also handle workspace_update for backward compatibility
        workspace_update = reasoning_data.get("workspace_update", {})
        if workspace_update and isinstance(workspace_update, dict):
            if "objective" in workspace_update:
                self.reasoning.goal = workspace_update["objective"]
            if "approach" in workspace_update:
                self.reasoning.strategy = workspace_update["approach"]
            if "observations" in workspace_update and isinstance(
                workspace_update["observations"], list
            ):
                for insight in workspace_update["observations"]:
                    self.reasoning.add_insight(insight)

        # Handle direct response - set if provided, prioritize tool calls over non-empty responses
        if "response" in reasoning_data:
            response_content = reasoning_data["response"]
            if not tool_calls or not response_content:
                # Set response if no tool calls, or if response is empty (allows clearing)
                self.execution.response = response_content

        # Handle mode switching - delegated to ModeController
        mode_field = reasoning_data.get("switch_mode") or reasoning_data.get("switch_to")
        switch_why = reasoning_data.get("switch_why", "")
        if mode_field and switch_why:
            import contextlib

            from cogency.steps.reason.modes import ModeController

            with contextlib.suppress(ValueError):
                # Use centralized mode switching logic
                current_mode = str(self.execution.mode)
                if ModeController.should_switch(
                    current_mode,
                    mode_field,
                    switch_why,
                    self.execution.iteration,
                    self.execution.max_iterations,
                ):
                    ModeController.execute_switch(self, mode_field, switch_why)

        # Store security assessment for tool execution
        if "security_assessment" in reasoning_data:
            self.execution.security_assessment = reasoning_data["security_assessment"]
