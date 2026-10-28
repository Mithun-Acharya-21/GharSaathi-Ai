import re
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel

# Unicode digit translation tables
KANNADA_DIGITS = str.maketrans("೦೧೨೩೪೫೬೭೮೯", "0123456789")
DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

# Word mappings for common numbers in English and Kannada
WORD_TO_NUMBER: dict[str, str] = {
    # English
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "twenty-one": "21",
    "twenty-two": "22",
    "twenty-three": "23",
    "twenty-four": "24",
    "thirty": "30",
    "thirty-four": "34",
    "thirty four": "34",
    # Kannada words
    "ಸೊನ್ನೆ": "0",
    "ಒಂದು": "1",
    "ಎರಡು": "2",
    "ಮೂರು": "3",
    "ನಾಲ್ಕು": "4",
    "ಐದು": "5",
    "ಆರು": "6",
    "ಏಳು": "7",
    "ಎಂಟು": "8",
    "ಒಂಬತ್ತು": "9",
    "ಹತ್ತು": "10",
    "ಹನ್ನೊಂದು": "11",
    "ಹನ್ನೆರಡು": "12",
    "ಹದಿಮೂರು": "13",
    "ಹದಿನಾಲ್ಕು": "14",
    "ಹದಿನೈದು": "15",
    "ಮೂವತ್ತುನಾಲ್ಕು": "34",
}


def normalize_numeric_string(raw: str) -> str:
    """Normalize digits from Kannada, Devanagari, or words to clean ASCII string."""
    if not raw:
        return ""
    text = raw.strip().translate(KANNADA_DIGITS).translate(DEVANAGARI_DIGITS)
    cleaned_lower = text.lower().strip()

    if cleaned_lower in WORD_TO_NUMBER:
        return WORD_TO_NUMBER[cleaned_lower]

    # Remove currency symbols and common unit indicators
    cleaned = re.sub(r"[₹$,\s]", "", text)
    return cleaned


class EvaluationResult(BaseModel):
    is_correct: bool
    feedback: str
    next_hint: str | None = None
    review_required: bool = False


class Evaluator:
    """Deterministic mathematical evaluator against server-side activity specifications."""

    @staticmethod
    def evaluate(
        question_type: str,
        confirmed_answer: Any,
        evaluator_config: dict[str, Any],
        hints: list[str] | None = None,
        hint_index: int = 0,
    ) -> EvaluationResult:
        hints = hints or []
        feedback_templates = evaluator_config.get("feedback_templates", {})
        correct_tmpl = feedback_templates.get(
            "correct", "Great job! Your mathematical thinking is spot on!"
        )
        incorrect_tmpl = feedback_templates.get(
            "incorrect", "Not quite yet. Let's look closely at the problem together."
        )

        next_hint = hints[hint_index] if hint_index < len(hints) else None

        if confirmed_answer is None or str(confirmed_answer).strip() == "":
            return EvaluationResult(
                is_correct=False,
                feedback="We could not detect an answer. Would you like to review or try again?",
                next_hint=next_hint,
                review_required=True,
            )

        try:
            if question_type == "integer":
                return Evaluator._evaluate_integer(
                    confirmed_answer, evaluator_config, correct_tmpl, incorrect_tmpl, next_hint
                )
            elif question_type == "decimal":
                return Evaluator._evaluate_decimal(
                    confirmed_answer, evaluator_config, correct_tmpl, incorrect_tmpl, next_hint
                )
            elif question_type == "multiple_choice":
                return Evaluator._evaluate_multiple_choice(
                    confirmed_answer, evaluator_config, correct_tmpl, incorrect_tmpl, next_hint
                )
            elif question_type == "step_by_step":
                return Evaluator._evaluate_step_by_step(
                    confirmed_answer, evaluator_config, correct_tmpl, incorrect_tmpl, next_hint
                )
            else:
                return EvaluationResult(
                    is_correct=False,
                    feedback="Unsupported question type requiring teacher review.",
                    next_hint=next_hint,
                    review_required=True,
                )
        except Exception:
            return EvaluationResult(
                is_correct=False,
                feedback="We encountered an issue interpreting this answer. A teacher can review it.",
                next_hint=next_hint,
                review_required=True,
            )

    @staticmethod
    def _evaluate_integer(
        raw_answer: Any,
        config: dict[str, Any],
        correct_tmpl: str,
        incorrect_tmpl: str,
        next_hint: str | None,
    ) -> EvaluationResult:
        normalized = normalize_numeric_string(str(raw_answer))
        # Extract digits if surrounded by text (e.g. "it is 12" or "ಉತ್ತರ 12")
        match = re.search(r"-?\d+", normalized)
        if not match:
            return EvaluationResult(
                is_correct=False,
                feedback="Please confirm a whole number for this answer.",
                next_hint=next_hint,
                review_required=True,
            )

        val = int(match.group())
        expected = int(config.get("expected_value", 0))
        is_correct = val == expected

        return EvaluationResult(
            is_correct=is_correct,
            feedback=correct_tmpl if is_correct else incorrect_tmpl,
            next_hint=None if is_correct else next_hint,
            review_required=False,
        )

    @staticmethod
    def _evaluate_decimal(
        raw_answer: Any,
        config: dict[str, Any],
        correct_tmpl: str,
        incorrect_tmpl: str,
        next_hint: str | None,
    ) -> EvaluationResult:
        normalized = normalize_numeric_string(str(raw_answer))
        match = re.search(r"-?\d+(\.\d+)?", normalized)
        if not match:
            return EvaluationResult(
                is_correct=False,
                feedback="Please confirm a numeric value with decimals if needed.",
                next_hint=next_hint,
                review_required=True,
            )

        try:
            val = Decimal(match.group())
            expected = Decimal(str(config.get("expected_value", "0.0")))
            tolerance = Decimal(str(config.get("tolerance", "0.00")))
            is_correct = abs(val - expected) <= tolerance

            return EvaluationResult(
                is_correct=is_correct,
                feedback=correct_tmpl if is_correct else incorrect_tmpl,
                next_hint=None if is_correct else next_hint,
                review_required=False,
            )
        except InvalidOperation:
            return EvaluationResult(
                is_correct=False,
                feedback="Could not parse decimal number.",
                next_hint=next_hint,
                review_required=True,
            )

    @staticmethod
    def _evaluate_multiple_choice(
        raw_answer: Any,
        config: dict[str, Any],
        correct_tmpl: str,
        incorrect_tmpl: str,
        next_hint: str | None,
    ) -> EvaluationResult:
        user_choice = str(raw_answer).strip().upper()
        expected = str(config.get("expected_value", "")).strip().upper()
        # Accept alternative label formats (e.g. "Option A" or "A")
        if user_choice.startswith("OPTION "):
            user_choice = user_choice.replace("OPTION ", "").strip()

        is_correct = user_choice == expected
        return EvaluationResult(
            is_correct=is_correct,
            feedback=correct_tmpl if is_correct else incorrect_tmpl,
            next_hint=None if is_correct else next_hint,
            review_required=False,
        )

    @staticmethod
    def _evaluate_step_by_step(
        raw_answer: Any,
        config: dict[str, Any],
        correct_tmpl: str,
        incorrect_tmpl: str,
        next_hint: str | None,
    ) -> EvaluationResult:
        """Handles structured questions like place value (e.g., tens=3, ones=4 or "3 tens and 4 ones")."""
        expected_steps = config.get("expected_steps", {})  # e.g. {"tens": 3, "ones": 4}
        if isinstance(raw_answer, dict):
            # Dict input: {"tens": 3, "ones": 4}
            all_match = True
            for k, expected_v in expected_steps.items():
                if k not in raw_answer or int(raw_answer[k]) != int(expected_v):
                    all_match = False
                    break
            return EvaluationResult(
                is_correct=all_match,
                feedback=correct_tmpl if all_match else incorrect_tmpl,
                next_hint=None if all_match else next_hint,
                review_required=False,
            )

        # String representation parsing
        text = str(raw_answer).lower().translate(KANNADA_DIGITS)
        # Look for numbers in text
        numbers = re.findall(r"\d+", text)
        if len(numbers) >= 2:
            tens_cand, ones_cand = int(numbers[0]), int(numbers[1])
            if tens_cand == expected_steps.get("tens") and ones_cand == expected_steps.get("ones"):
                return EvaluationResult(
                    is_correct=True,
                    feedback=correct_tmpl,
                    next_hint=None,
                    review_required=False,
                )

        # Check total value if provided directly (e.g. 34)
        if "total" in config and numbers:
            total_cand = int(numbers[0])
            if total_cand == int(config["total"]):
                return EvaluationResult(
                    is_correct=True,
                    feedback=correct_tmpl,
                    next_hint=None,
                    review_required=False,
                )

        return EvaluationResult(
            is_correct=False,
            feedback=incorrect_tmpl,
            next_hint=next_hint,
            review_required=False,
        )
