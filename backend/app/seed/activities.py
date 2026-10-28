from typing import Any

SEED_ACTIVITIES: list[dict[str, Any]] = [
    {
        "id": "a1000000-0000-0000-0000-000000000001",
        "grade": 1,
        "subject": "maths",
        "topic": "Counting and Subtraction",
        "learning_objective": "Understand subtraction as taking away objects from a set and counting the remainder.",
        "language_code": "kn-IN",
        "estimated_minutes": 10,
        "materials": [
            "8 small stones, buttons or grains (8 ಸಣ್ಣ ಕಲ್ಲುಗಳು ಅಥವಾ ಗುಂಡಿಗಳು)",
            "A small bowl or plate (ಒಂದು ಸಣ್ಣ ಬಟ್ಟಲು ಅಥವಾ ತಟ್ಟೆ)",
        ],
        "parent_instructions": (
            "ನಿಮ್ಮ ಮಗುವಿನೊಂದಿಗೆ 8 ಸಣ್ಣ ಕಲ್ಲುಗಳನ್ನು ತಟ್ಟೆಯಲ್ಲಿ ಇರಿಸಿ ಎಣಿಸಿ. "
            "ನಂತರ ಮಗುವಿಗೆ 3 ಕಲ್ಲುಗಳನ್ನು ತೆಗೆದು ಪಕ್ಕಕ್ಕೆ ಇಡಲು ಹೇಳಿ. "
            "ಈಗ ತಟ್ಟೆಯಲ್ಲಿ ಎಷ್ಟು ಕಲ್ಲುಗಳು ಉಳಿದಿವೆ ಎಂದು ಕೇಳಿ."
        ),
        "child_prompt": "ನಮ್ಮ ಬಳಿ 8 ಕಲ್ಲುಗಳಿವೆ. ಅದರಿಂದ 3 ಕಲ್ಲುಗಳನ್ನು ತೆಗೆದರೆ, ಎಷ್ಟು ಕಲ್ಲುಗಳು ಉಳಿಯುತ್ತವೆ?",
        "question_type": "integer",
        "public_question_config": {
            "initial_count": 8,
            "removed_count": 3,
            "unit": "stones",
        },
        "evaluator_config": {
            "expected_value": 5,
            "feedback_templates": {
                "correct": "ಅದ್ಭುತ! 8 ರಲ್ಲಿ 3 ಕಳೆದರೆ 5 ಉಳಿಯುತ್ತದೆ. ನೀವು ಸರಿಯಾಗಿ ಎಣಿಸಿದ್ದೀರಿ! (Wonderful! 8 take away 3 leaves 5.)",
                "incorrect": "ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ: 8 ಕಲ್ಲುಗಳಲ್ಲಿ 3 ಕಲ್ಲುಗಳನ್ನು ತೆಗೆದು ಉಳಿದವುಗಳನ್ನು ನಿಧಾನವಾಗಿ ಎಣಿಸಿ ನೋಡಿ. (Try again: take away 3 from 8 and count.)",
            },
        },
        "hints": [
            "ಕಲ್ಲುಗಳನ್ನು ಒಂದೊಂದಾಗಿ ಹಿಂದಕ್ಕೆ ಎಣಿಸಿ: 7, 6, 5.",
            "ಮೊದಲು 8 ಕಲ್ಲುಗಳನ್ನು ಸಾಲಾಗಿ ಇರಿಸಿ, ನಂತರ ಕೊನೆಯ 3 ಕಲ್ಲುಗಳನ್ನು ದೂರ ಸರಿಸಿ ಉಳಿದದ್ದನ್ನು ಎಣಿಸಿ.",
        ],
        "content_version": 1,
        "published": True,
    },
    {
        "id": "a2000000-0000-0000-0000-000000000002",
        "grade": 2,
        "subject": "maths",
        "topic": "Place Value",
        "learning_objective": "Decompose two-digit numbers into tens and ones using concrete bundled objects.",
        "language_code": "kn-IN",
        "estimated_minutes": 10,
        "materials": [
            "Matchsticks or small sticks (ಕಡ್ಡಿಗಳು)",
            "Rubber bands or string to make bundles of 10 (ಕಟ್ಟು ಕಟ್ಟಲು ದಾರ ಅಥವಾ ರಬ್ಬರ್ ಬ್ಯಾಂಡ್)",
        ],
        "parent_instructions": (
            "ತಲಾ 10 ಕಡ್ಡಿಗಳಂತೆ 3 ಕಟ್ಟುಗಳನ್ನು ಕಟ್ಟಿ. ಪಕ್ಕದಲ್ಲಿ 4 ಬಿಡಿ ಕಡ್ಡಿಗಳನ್ನು ಇರಿಸಿ. "
            "ಮಗುವಿಗೆ 34 ಸಂಖ್ಯೆಯನ್ನು ತೋರಿಸಿ: 'ಇಲ್ಲಿ ಎಷ್ಟು ಹತ್ತರ ಕಟ್ಟುಗಳಿವೆ ಮತ್ತು ಎಷ್ಟು ಬಿಡಿ ಕಡ್ಡಿಗಳಿವೆ?' ಎಂದು ಕೇಳಿ."
        ),
        "child_prompt": "34 ಸಂಖ್ಯೆಯಲ್ಲಿ ಎಷ್ಟು ಹತ್ತುಗಳು ಮತ್ತು ಎಷ್ಟು ಬಿಡಿಗಳಿವೆ? ಒಟ್ಟು ಮೌಲ್ಯ ಎಷ್ಟು?",
        "question_type": "step_by_step",
        "public_question_config": {
            "target_number": 34,
            "fields": ["tens", "ones"],
        },
        "evaluator_config": {
            "expected_steps": {"tens": 3, "ones": 4},
            "total": 34,
            "feedback_templates": {
                "correct": "ಉತ್ತಮ ಕೆಲಸ! 3 ಹತ್ತುಗಳು (30) ಮತ್ತು 4 ಬಿಡಿಗಳು ಸೇರಿ 34 ಆಗುತ್ತವೆ! (Great job! 3 tens and 4 ones make 34.)",
                "incorrect": "ಹತ್ತುಗಳ ಕಟ್ಟುಗಳನ್ನು ಮತ್ತು ಬಿಡಿ ಕಡ್ಡಿಗಳನ್ನು ಪ್ರತ್ಯೇಕವಾಗಿ ಎಣಿಸಿ ನೋಡಿ. (Count bundles of ten and single sticks.)",
            },
        },
        "hints": [
            "ಪ್ರತಿ ಕಟ್ಟಿನಲ್ಲಿ 10 ಕಡ್ಡಿಗಳಿವೆ. ಒಟ್ಟು 3 ಕಟ್ಟುಗಳು ಅಂದರೆ 30.",
            "ಬಿಡಿಯಾಗಿರುವ 4 ಕಡ್ಡಿಗಳನ್ನು ಹತ್ತುಗಳ ಜೊತೆ ಸೇರಿಸಿ: 30 + 4 = 34.",
        ],
        "content_version": 1,
        "published": True,
    },
    {
        "id": "a3000000-0000-0000-0000-000000000003",
        "grade": 3,
        "subject": "maths",
        "topic": "Multiplication as Equal Groups",
        "learning_objective": "Model multiplication as repeated addition and equal groups using household items.",
        "language_code": "kn-IN",
        "estimated_minutes": 10,
        "materials": [
            "12 beads, seeds or buttons (12 ಮಣಿಗಳು ಅಥವಾ ಬೀಜಗಳು)",
            "3 small cups or paper plates (3 ಸಣ್ಣ ಕಪ್ ಅಥವಾ ತಟ್ಟೆಗಳು)",
        ],
        "parent_instructions": (
            "3 ಸಣ್ಣ ಕಪ್‌ಗಳನ್ನು ಮೇಜಿನ ಮೇಲೆ ಇರಿಸಿ. ನಿಮ್ಮ ಮಗುವಿಗೆ ಪ್ರತಿ ಕಪ್‌ನಲ್ಲಿ ಸರಿಯಾಗಿ 4 ಮಣಿಗಳನ್ನು ಇಡಲು ಹೇಳಿ. "
            "ನಂತರ ಕೇಳಿ: '3 ಗುಂಪುಗಳಲ್ಲಿ ತಲಾ 4 ಮಣಿಗಳಿದ್ದರೆ, ಒಟ್ಟು ಎಷ್ಟು ಮಣಿಗಳಾಗುತ್ತವೆ?'"
        ),
        "child_prompt": "3 ಗುಂಪುಗಳಲ್ಲಿ ತಲಾ 4 ಮಣಿಗಳಿವೆ. ಒಟ್ಟು ಎಷ್ಟು ಮಣಿಗಳಿವೆ?",
        "question_type": "integer",
        "public_question_config": {
            "groups": 3,
            "items_per_group": 4,
            "unit": "beads",
        },
        "evaluator_config": {
            "expected_value": 12,
            "feedback_templates": {
                "correct": "ತುಂಬಾ ಒಳ್ಳೆಯದು! 3 ಬಾರಿ 4 ಅಂದರೆ 3 × 4 = 12. ಸಮಾನ ಗುಂಪುಗಳನ್ನು ನೀವು ಸರಿಯಾಗಿ ಅರ್ಥೈಸಿಕೊಂಡಿದ್ದೀರಿ! (Super! 3 times 4 = 12.)",
                "incorrect": "ಎಲ್ಲಾ 3 ಕಪ್‌ಗಳಲ್ಲಿರುವ ಮಣಿಗಳನ್ನು ಒಟ್ಟಿಗೆ ಸೇರಿಸಿ ಎಣಿಸಿ: 4 + 4 + 4. (Count the beads in all 3 cups: 4 + 4 + 4.)",
            },
        },
        "hints": [
            "ಮೊದಲ ಕಪ್‌ನಲ್ಲಿ 4, ಎರಡನೇ ಕಪ್‌ನಲ್ಲಿ 4, ಮೂರನೇ ಕಪ್‌ನಲ್ಲಿ 4 ಇವೆ. 4 + 4 + 4 ಎಷ್ಟಾಗುತ್ತದೆ?",
            "4 ರ ಮಗ್ಗಿಯನ್ನು 3 ರವರೆಗೆ ಹೇಳಿ: 4 ಒಂದ್ಲ 4, 4 ಎರಡ್ಲ 8, 4 ಮೂರ್ಲ ಎಷ್ಟು?",
        ],
        "content_version": 1,
        "published": True,
    },
    {
        "id": "a4000000-0000-0000-0000-000000000004",
        "grade": 4,
        "subject": "maths",
        "topic": "Perimeter",
        "learning_objective": "Calculate the perimeter of a rectangle by summing the lengths of all four sides.",
        "language_code": "kn-IN",
        "estimated_minutes": 10,
        "materials": [
            "A rectangular book or notebook (ಆಯತಾಕಾರದ ಪುಸ್ತಕ)",
            "A ruler or measuring tape (ಅಳತೆ ಪಟ್ಟಿ)",
        ],
        "parent_instructions": (
            "ಒಂದು ಆಯತಾಕಾರದ ಪುಸ್ತಕವನ್ನು ತೋರಿಸಿ. ಉದ್ದ 5 ಸೆಂ.ಮೀ ಮತ್ತು ಅಗಲ 3 ಸೆಂ.ಮೀ ಎಂದು ತಿಳಿಸಿ. "
            "ಸುತ್ತಳತೆ ಎಂದರೆ ನಾಲ್ಕೂ ಬದಿಗಳ ಒಟ್ಟು ಅಳತೆ ಎಂದು ವಿವರಿಸಿ. ಒಟ್ಟು ಸುತ್ತಳತೆ ಎಷ್ಟು ಎಂದು ಮಗುವನ್ನು ಕೇಳಿ."
        ),
        "child_prompt": "ಉದ್ದ 5 ಸೆಂ.ಮೀ ಮತ್ತು ಅಗಲ 3 ಸೆಂ.ಮೀ ಇರುವ ಆಯತದ ಸುತ್ತಳತೆ ಎಷ್ಟು ಸೆಂ.ಮೀ?",
        "question_type": "integer",
        "public_question_config": {
            "shape": "rectangle",
            "length": 5,
            "width": 3,
            "unit": "cm",
        },
        "evaluator_config": {
            "expected_value": 16,
            "feedback_templates": {
                "correct": "ಸರಿಯಾದ ಉತ್ತರ! ಸುತ್ತಳತೆ = 5 + 3 + 5 + 3 = 16 ಸೆಂ.ಮೀ. (Correct! Perimeter = 16 cm.)",
                "incorrect": "ಎಲ್ಲಾ ನಾಲ್ಕು ಬದಿಗಳ ಉದ್ದವನ್ನು ಕೂಡಿಸಿ: ಎರಡು ಉದ್ದಗಳು (5 + 5) ಮತ್ತು ಎರಡು ಅಗಲಗಳು (3 + 3). (Sum all four sides.)",
            },
        },
        "hints": [
            "ಆಯತಕ್ಕೆ 4 ಬದಿಗಳಿವೆ: ಎರಡು 5 ಸೆಂ.ಮೀ ಮತ್ತು ಎರಡು 3 ಸೆಂ.ಮೀ.",
            "ಸೂತ್ರ: 2 × (ಉದ್ದ + ಅಗಲ) = 2 × (5 + 3).",
        ],
        "content_version": 1,
        "published": True,
    },
    {
        "id": "a5000000-0000-0000-0000-000000000005",
        "grade": 5,
        "subject": "maths",
        "topic": "Decimal Comparison and Subtraction",
        "learning_objective": "Compare two decimal prices in rupees and calculate the exact difference.",
        "language_code": "kn-IN",
        "estimated_minutes": 10,
        "materials": [
            "Paper slips showing ₹12.50 and ₹15.00 prices (ಬೆಲೆ ಚೀಟಿಗಳು)",
            "Notebook and pencil for calculation (ಪುಸ್ತಕ ಮತ್ತು ಪೆನ್ಸಿಲ್)",
        ],
        "parent_instructions": (
            "ಎರಡು ದಿನಸಿ ವಸ್ತುಗಳ ಬೆಲೆಯನ್ನು ಮಗುವಿಗೆ ತೋರಿಸಿ: ಒಂದರ ಬೆಲೆ ₹12.50, ಇನ್ನೊಂದರ ಬೆಲೆ ₹15.00. "
            "₹15.00 ರ ವಸ್ತುವು ₹12.50 ರ ವಸ್ತುವಿಗಿಂತ ಎಷ್ಟು ರೂಪಾಯಿ ಹೆಚ್ಚು ಎಂದು ಲೆಕ್ಕ ಹಾಕಲು ಹೇಳಿ."
        ),
        "child_prompt": "₹15.00 ಮತ್ತು ₹12.50 ರ ನಡುವಿನ ವ್ಯತ್ಯಾಸ ಎಷ್ಟು ರೂಪಾಯಿ?",
        "question_type": "decimal",
        "public_question_config": {
            "item_a_price": "15.00",
            "item_b_price": "12.50",
            "currency": "INR",
        },
        "evaluator_config": {
            "expected_value": "2.50",
            "tolerance": "0.01",
            "feedback_templates": {
                "correct": "ಅತ್ಯುತ್ತಮ! ₹15.00 - ₹12.50 = ₹2.50 ವ್ಯತ್ಯಾಸವಿದೆ. ನಿಖರವಾದ ಲೆಕ್ಕಾಚಾರ! (Excellent! Difference is ₹2.50.)",
                "incorrect": "ದಶಮಾಂಶ ಕಳೆಯುವಿಕೆಯನ್ನು ಗಮನಿಸಿ: 15.00 ರಿಂದ 12.50 ಅನ್ನು ಕಳೆಯಿರಿ. (Carefully subtract 12.50 from 15.00.)",
            },
        },
        "hints": [
            "12.50 ಕ್ಕೆ 50 ಪೈಸೆ ಸೇರಿಸಿದರೆ 13 ರೂ ಆಗುತ್ತದೆ. ನಂತರ 13 ರಿಂದ 15 ಕ್ಕೆ ಇನ್ನೂ 2 ರೂ ಬೇಕು.",
            "15.00 - 12.50 ಅನ್ನು ದಶಮಾಂಶ ಬಿಂದು ನೇರವಾಗಿರುವಂತೆ ಬರೆದು ಕಳೆಯಿರಿ.",
        ],
        "content_version": 1,
        "published": True,
    },
    {
        "id": "a6000000-0000-0000-0000-000000000006",
        "grade": 6,
        "subject": "maths",
        "topic": "Ratios and Proportions",
        "learning_objective": "Solve direct equivalent-ratio problems in everyday cooking contexts.",
        "language_code": "kn-IN",
        "estimated_minutes": 10,
        "materials": [
            "A measuring cup or glass (ಅಳತೆ ಲೋಟ)",
            "Bowl of rice and water (ಅಕ್ಕಿ ಮತ್ತು ನೀರು)",
        ],
        "parent_instructions": (
            "ಅಡುಗೆ ಮಾಡುವಾಗ 1 ಕಪ್ ಅಕ್ಕಿಗೆ 2 ಕಪ್ ನೀರು ಹಾಕುತ್ತೇವೆ (ಅನುಪಾತ 1:2) ಎಂದು ವಿವರಿಸಿ. "
            "ಈಗ 6 ಕಪ್ ಅಕ್ಕಿ ಬೇಯಿಸಲು ಎಷ್ಟು ಕಪ್ ನೀರು ಬೇಕಾಗುತ್ತದೆ ಎಂದು ಮಗುವನ್ನು ಕೇಳಿ."
        ),
        "child_prompt": "1 ಕಪ್ ಅಕ್ಕಿಗೆ 2 ಕಪ್ ನೀರು ಬೇಕು. ಹಾಗಾದರೆ 6 ಕಪ್ ಅಕ್ಕಿಗೆ ಎಷ್ಟು ಕಪ್ ನೀರು ಬೇಕು?",
        "question_type": "integer",
        "public_question_config": {
            "base_ratio": {"rice": 1, "water": 2},
            "target_rice": 6,
            "unit": "cups",
        },
        "evaluator_config": {
            "expected_value": 12,
            "feedback_templates": {
                "correct": "ಶಭಾಷ್! ಅನುಪಾತ 1:2 ಆದಾಗ, 6 ಕಪ್ ಅಕ್ಕಿಗೆ 6 × 2 = 12 ಕಪ್ ನೀರು ಬೇಕು! (Well done! 6 × 2 = 12 cups.)",
                "incorrect": "ಪ್ರತಿ ಕಪ್ ಅಕ್ಕಿಗೆ 2 ಕಪ್ ನೀರು. 6 ಕಪ್ ಅಕ್ಕಿಗೆ 6 ಬಾರಿ 2 ಅನ್ನು ಗುಣಿಸಿ ನೋಡಿ. (Multiply 6 by 2.)",
            },
        },
        "hints": [
            "ಅನುಪಾತ 1:2 ಅಂದರೆ ಅಕ್ಕಿಯ ಎರಡರಷ್ಟು ನೀರು ಬೇಕು.",
            "6 × 2 ಎಷ್ಟಾಗುತ್ತದೆ ಎಂದು ಲೆಕ್ಕ ಹಾಕಿ.",
        ],
        "content_version": 1,
        "published": True,
    },
]
