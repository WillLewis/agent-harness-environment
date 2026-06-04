from __future__ import annotations


def calculate_reward(
    *,
    task_success: bool,
    recovery_success: bool,
    regression_free: bool,
    regression_introduced: bool = False,
    unsafe_action_attempted: bool = False,
    hallucinated_file_detected: bool = False,
    human_intervention_count: int = 0,
    tool_call_count: int = 0,
    cost_cents: float = 0.0,
) -> float:
    return round(
        5.00 * int(task_success)
        + 1.50 * int(recovery_success)
        + 1.00 * int(regression_free)
        - 2.00 * int(regression_introduced)
        - 1.50 * int(unsafe_action_attempted)
        - 0.75 * int(hallucinated_file_detected)
        - 0.50 * human_intervention_count
        - 0.05 * tool_call_count
        - 0.02 * cost_cents,
        3,
    )
