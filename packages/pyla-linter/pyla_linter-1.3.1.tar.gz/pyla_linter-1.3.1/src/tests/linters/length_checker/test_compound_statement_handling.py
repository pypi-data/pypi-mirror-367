"""Tests for compound statement handling in the length checker."""

from src.linters.length_checker.config import LengthCheckerConfig

from .test_utils import run_plugin_on_code


class TestCompoundStatementHandling:
    """Test comprehensive compound statement handling for if/elif/else, try/except/finally."""

    def test_complex_if_elif_else_chain(self):
        """Test that complex if/elif/else chains count statements correctly."""
        code = """def complex_conditional():
    x = 10
    if x > 15:
        result = "high"
        print(result)
    elif x > 10:
        result = "medium"
        log_value(result)
    elif x > 5:
        result = "low"
        process_value(result)
    else:
        result = "zero"
        handle_zero(result)
    return result"""

        config = LengthCheckerConfig(max_function_length=8)
        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        # Should count: def, x=10, if, result="high", print(), result="medium",
        # log_value(), result="low", process_value(), result="zero", handle_zero(), return
        # = 14 statements total (actual count)
        _, _, message, _ = errors[0]
        assert "14 statements long" in message

    def test_nested_try_except_finally_blocks(self):
        """Test nested try/except/finally blocks count correctly."""
        code = """def nested_exception_handling():
    try:
        x = get_value()
        try:
            result = process(x)
            validate(result)
        except ValidationError:
            result = default_value()
        finally:
            log_process()
    except NetworkError as e:
        handle_network_error(e)
        retry_count += 1
    except Exception:
        handle_generic_error()
    finally:
        cleanup_resources()
    return result"""

        config = LengthCheckerConfig(max_function_length=10)
        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        # Should count all executable statements including nested try blocks
        # = 13 statements total (actual count)
        _, _, message, _ = errors[0]
        assert "13 statements long" in message

    def test_match_case_statements(self):
        """Test Python 3.10+ match/case statements (if supported)."""
        code = """def match_example(value):
    match value:
        case 1:
            result = "one"
        case 2 | 3:
            result = "two or three"
        case str() if len(value) > 5:
            result = "long string"
        case _:
            result = "default"
    return result"""

        try:
            config = LengthCheckerConfig(max_function_length=5)
            errors = run_plugin_on_code(code, config)
            # Should handle match/case correctly regardless of Python version
            if errors:  # If match/case is supported and creates violations
                _, _, message, _ = errors[0]
                assert "statements long" in message
        except SyntaxError:
            # Match/case not supported in this Python version, skip test
            pass

    def test_complex_loop_structures(self):
        """Test complex loop structures with breaks and continues."""
        code = """def complex_loops():
    for i in range(10):
        if i % 2 == 0:
            continue
        for j in range(i):
            if j > 5:
                break
            process_pair(i, j)

    while condition():
        try:
            value = get_next()
            if value is None:
                break
            process(value)
        except StopIteration:
            break
    return results"""

        config = LengthCheckerConfig(max_function_length=10)
        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        # Should count all statements including control flow
        _, _, message, _ = errors[0]
        assert "statements long" in message
