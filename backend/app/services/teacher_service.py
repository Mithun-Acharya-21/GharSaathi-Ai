from app.repositories.attempt_repository import AttemptRepository
from app.repositories.teacher_repository import TeacherRepository
from app.schemas.teacher import ReviewQueueItem, TeacherReportResponse, TopicMetric


class TeacherService:
    def __init__(
        self,
        teacher_repo: TeacherRepository,
        attempt_repo: AttemptRepository,
    ):
        self.teacher_repo = teacher_repo
        self.attempt_repo = attempt_repo

    async def get_reports(self, grade: int | None = None) -> TeacherReportResponse:
        data = await self.teacher_repo.get_aggregate_report(grade=grade)
        topic_metrics = [TopicMetric(**t) for t in data["topics"]]
        return TeacherReportResponse(
            grade=data["grade"],
            activities_available=data["activities_available"],
            sessions_started=data["sessions_started"],
            sessions_completed=data["sessions_completed"],
            attempts_evaluated=data["attempts_evaluated"],
            correct_evaluated_attempts=data["correct_evaluated_attempts"],
            incorrect_evaluated_attempts=data["incorrect_evaluated_attempts"],
            overall_accuracy_percentage=data["overall_accuracy_percentage"],
            review_required_count=data["review_required_count"],
            topics=topic_metrics,
        )

    async def get_review_queue(self, grade: int | None = None) -> list[ReviewQueueItem]:
        attempts = await self.attempt_repo.get_review_queue(grade=grade)
        items: list[ReviewQueueItem] = []
        for att in attempts:
            session = att.session
            activity = session.activity if session else None
            items.append(
                ReviewQueueItem(
                    attempt_id=att.id,
                    grade=activity.grade if activity else 0,
                    topic=activity.topic if activity else "Unknown",
                    child_prompt=activity.child_prompt if activity else "",
                    input_mode=att.input_mode,
                    draft_transcript=att.draft_transcript,
                    confirmed_transcript=att.confirmed_transcript,
                    confirmed_answer=att.confirmed_answer,
                    evaluation_status=att.evaluation_status,
                    feedback=att.feedback,
                    created_at=att.created_at,
                )
            )
        return items
