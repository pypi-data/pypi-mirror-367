"""State persistence utilities."""

from typing import Dict

from cogency.state import AgentState


async def _get_state(
    user_id: str,
    query: str,
    max_iterations: int,
    user_states: Dict[str, AgentState],
    persistence=None,
) -> AgentState:
    """Internal: Get existing state or restore from persistence, creating new if needed."""

    # Check existing in-memory state first
    state = user_states.get(user_id)
    if state:
        # Reset execution state for new query to prevent response caching
        from cogency.state.execution import ExecutionState

        # Preserve conversation history from previous execution
        previous_messages = state.execution.messages if state.execution else []

        state.execution = ExecutionState(query=query, user_id=user_id)
        state.execution.max_iterations = max_iterations

        # Restore conversation history
        state.execution.messages = previous_messages

        return state

    # Try to restore from persistence
    if persistence:
        state = await persistence.load(user_id)

        if state:
            # Update query for restored state
            state.execution.query = query
            user_states[user_id] = state
            return state

    # Create new state if restore failed or persistence disabled
    state = AgentState(query=query, user_id=user_id)
    state.execution.max_iterations = max_iterations
    user_states[user_id] = state
    return state
