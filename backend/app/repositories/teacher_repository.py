from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import EvaluationStatus, SessionStatus
from app.models.activity import Activity
from app.models.attempt import Attempt
from app.models.session import Session


class TeacherRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_aggregate_report(self, grade: int | None = None) -> dict[str, Any]:
        # 1. Total published activities count
        act_query = select(func.count(Activity.id)).where(Activity.published.is_(True))
        if grade is not None:
            act_query = act_query.where(Activity.grade == grade)
        act_result = await self.session.execute(act_query)
        activities_available = act_result.scalar_one() or 0

        # 2. Session counts
        sess_query = select(
            func.count(Session.id).label("started"),
            func.count(case((Session.status == SessionStatus.COMPLETED.value, 1))).label(
                "completed"
            ),
        ).join(Activity, Session.activity_id == Activity.id)
        if grade is not None:
            sess_query = sess_query.where(Activity.grade == grade)
        sess_res = await self.session.execute(sess_query)
        sess_row = sess_res.one()
        sessions_started = sess_row.started or 0
        sessions_completed = sess_row.completed or 0

        # 3. Attempt counts
        att_query = (
            select(
                func.count(
                    case((Attempt.evaluation_status == EvaluationStatus.EVALUATED.value, 1))
                ).label("evaluated"),
                func.count(
                    case(
                        (
                            (Attempt.evaluation_status == EvaluationStatus.EVALUATED.value)
                            & (Attempt.is_correct.is_(True)),
                            1,
                        )
                    )
                ).label("correct"),
                func.count(
                    case(
                        (
                            (Attempt.evaluation_status == EvaluationStatus.EVALUATED.value)
                            & (Attempt.is_correct.is_(False)),
                            1,
                        )
                    )
                ).label("incorrect"),
                func.count(
                    case((Attempt.evaluation_status == EvaluationStatus.REVIEW_REQUIRED.value, 1))
                ).label("review_required"),
            )
            .join(Session, Attempt.session_id == Session.id)
            .join(Activity, Session.activity_id == Activity.id)
        )
        if grade is not None:
            att_query = att_query.where(Activity.grade == grade)
        att_res = await self.session.execute(att_query)
        att_row = att_res.one()

        attempts_evaluated = att_row.evaluated or 0
        correct_evaluated = att_row.correct or 0
        incorrect_evaluated = att_row.incorrect or 0
        review_required_count = att_row.review_required or 0

        overall_accuracy = (
            round((correct_evaluated / attempts_evaluated) * 100.0, 1)
            if attempts_evaluated > 0
            else 0.0
        )

        # 4. Grouped by topic and grade
        topic_query = (
            select(
                Activity.grade,
                Activity.topic,
                func.count(func.distinct(Session.id)).label("sessions_started"),
                func.count(
                    func.distinct(
                        case((Session.status == SessionStatus.COMPLETED.value, Session.id))
                    )
                ).label("sessions_completed"),
                func.count(
                    case((Attempt.evaluation_status == EvaluationStatus.EVALUATED.value, 1))
                ).label("evaluated"),
                func.count(
                    case(
                        (
                            (Attempt.evaluation_status == EvaluationStatus.EVALUATED.value)
                            & (Attempt.is_correct.is_(True)),
                            1,
                        )
                    )
                ).label("correct"),
                func.count(
                    case((Attempt.evaluation_status == EvaluationStatus.REVIEW_REQUIRED.value, 1))
                ).label("review_required"),
            )
            .join(Session, Activity.id == Session.activity_id, isouter=True)
            .join(Attempt, Session.id == Attempt.session_id, isouter=True)
            .where(Activity.published.is_(True))
        )
        if grade is not None:
            topic_query = topic_query.where(Activity.grade == grade)

        topic_query = topic_query.group_by(Activity.grade, Activity.topic).order_by(
            Activity.grade, Activity.topic
        )
        topic_res = await self.session.execute(topic_query)
        topic_rows = topic_res.all()

        topics = []
        for r in topic_rows:
            t_evaluated = r.evaluated or 0
            t_correct = r.correct or 0
            t_acc = round((t_correct / t_evaluated) * 100.0, 1) if t_evaluated > 0 else 0.0
            topics.append(
                {
                    "grade": r.grade,
                    "topic": r.topic,
                    "sessions_started": r.sessions_started or 0,
                    "sessions_completed": r.sessions_completed or 0,
                    "attempts_evaluated": t_evaluated,
                    "correct_attempts": t_correct,
                    "accuracy_percentage": t_acc,
                    "review_required_count": r.review_required or 0,
                }
            )

        return {
            "grade": grade,
            "activities_available": activities_available,
            "sessions_started": sessions_started,
            "sessions_completed": sessions_completed,
            "attempts_evaluated": attempts_evaluated,
            "correct_evaluated_attempts": correct_evaluated,
            "incorrect_evaluated_attempts": incorrect_evaluated,
            "overall_accuracy_percentage": overall_accuracy,
            "review_required_count": review_required_count,
            "topics": topics,
        }
