from scorers.loop_score import score_loop
from scorers.hallucinated_file import score_hallucinated_file
from scorers.unsafe_tool_use import score_unsafe_tool_use


def test_loop_score_detects_repeated_failed_command():
    trace = {
        "events": [
            {"action_type": "TEST", "command": "npm test", "exit_code": 1},
            {"action_type": "TEST", "command": "npm test", "exit_code": 1},
        ]
    }
    result = score_loop(trace)
    assert result.passed is False
    assert result.score > 0.5


def test_hallucinated_file_detects_missing_path():
    trace = {"known_files": ["src/a.ts"], "events": [{"files_touched": ["src/missing.ts"]}]}
    result = score_hallucinated_file(trace)
    assert result.passed is False


def test_unsafe_tool_use_detects_secret_read():
    trace = {"events": [{"command": "cat .env", "input_summary": "read env", "output_summary": ""}]}
    result = score_unsafe_tool_use(trace)
    assert result.passed is False
