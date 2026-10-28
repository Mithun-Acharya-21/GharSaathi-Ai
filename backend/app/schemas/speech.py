from pydantic import BaseModel, Field


class SpeechSynthesizeRequest(BaseModel):
    activity_id: str = Field(
        ..., description="ID of the activity whose instructions/prompts to speak"
    )
    text_type: str = Field(
        default="instructions",
        description="Type of activity text to speak: 'instructions' or 'prompt'",
    )
    language_code: str = Field(default="kn-IN", description="Language code (e.g. kn-IN, en-IN)")
