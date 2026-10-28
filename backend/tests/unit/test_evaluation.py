from app.domain.evaluation import Evaluator, normalize_numeric_string


def test_normalize_numeric_string():
    # Kannada digits
    assert normalize_numeric_string("೧೨") == "12"
    assert normalize_numeric_string("೫") == "5"
    assert normalize_numeric_string("೩೪") == "34"

    # Devanagari digits
    assert normalize_numeric_string("१२") == "12"

    # Words
    assert normalize_numeric_string("twelve") == "12"
    assert normalize_numeric_string("ಹನ್ನೆರಡು") == "12"
    assert normalize_numeric_string("five") == "5"

    # Currency symbols & spaces
    assert normalize_numeric_string("₹ 2.50") == "2.50"


def test_evaluate_integer_correct():
    config = {
        "expected_value": 12,
        "feedback_templates": {
            "correct": "Super! 3 times 4 = 12.",
            "incorrect": "Try counting all beads.",
        },
    }
    # Direct integer
    res1 = Evaluator.evaluate("integer", 12, config)
    assert res1.is_correct is True
    assert "Super!" in res1.feedback
    assert res1.review_required is False

    # Spoken string in English
    res2 = Evaluator.evaluate("integer", "12", config)
    assert res2.is_correct is True

    # Spoken in Kannada numerals
    res3 = Evaluator.evaluate("integer", "೧೨", config)
    assert res3.is_correct is True

    # Spoken number word
    res4 = Evaluator.evaluate("integer", "twelve", config)
    assert res4.is_correct is True


def test_evaluate_integer_incorrect_with_hints():
    config = {
        "expected_value": 12,
        "feedback_templates": {
            "correct": "Correct!",
            "incorrect": "Try again.",
        },
    }
    hints = ["Hint 1: 4 + 4 + 4", "Hint 2: 4 x 3"]
    res = Evaluator.evaluate("integer", 10, config, hints=hints, hint_index=0)
    assert res.is_correct is False
    assert res.feedback == "Try again."
    assert res.next_hint == "Hint 1: 4 + 4 + 4"
    assert res.review_required is False


def test_evaluate_decimal():
    config = {
        "expected_value": "2.50",
        "tolerance": "0.01",
        "feedback_templates": {
            "correct": "Exact difference is 2.50",
            "incorrect": "Check subtraction.",
        },
    }
    res_correct = Evaluator.evaluate("decimal", "2.50", config)
    assert res_correct.is_correct is True

    res_with_rupee = Evaluator.evaluate("decimal", "₹2.50", config)
    assert res_with_rupee.is_correct is True

    res_wrong = Evaluator.evaluate("decimal", "3.00", config)
    assert res_wrong.is_correct is False


def test_evaluate_step_by_step_place_value():
    config = {
        "expected_steps": {"tens": 3, "ones": 4},
        "total": 34,
        "feedback_templates": {
            "correct": "Great place value work!",
            "incorrect": "Count tens and ones.",
        },
    }
    # Dict input
    res1 = Evaluator.evaluate("step_by_step", {"tens": 3, "ones": 4}, config)
    assert res1.is_correct is True

    # String input with 3 tens and 4 ones
    res2 = Evaluator.evaluate("step_by_step", "3 tens and 4 ones", config)
    assert res2.is_correct is True

    # Total 34 directly
    res3 = Evaluator.evaluate("step_by_step", "34", config)
    assert res3.is_correct is True


def test_evaluate_ambiguous_requires_review():
    config = {"expected_value": 12}
    res_empty = Evaluator.evaluate("integer", "", config)
    assert res_empty.review_required is True

    res_unclear = Evaluator.evaluate("integer", "maybe bananas", config)
    assert res_unclear.review_required is True
