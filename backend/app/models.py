from pydantic import BaseModel, EmailStr, Field, model_validator


class GenerateRequest(BaseModel):
    notes: str = Field(..., min_length=20)


class Flashcard(BaseModel):
    question: str
    answer: str


class MCQ(BaseModel):
    question: str
    options: list[str] = Field(..., min_length=4, max_length=4)
    answer: str


class StudyMaterial(BaseModel):
    summary: str
    flashcards: list[Flashcard]
    mcqs: list[MCQ]
    revision_points: list[str]

    @model_validator(mode="after")
    def ensure_not_empty(self):
        has_content = any(
            [
                self.summary.strip(),
                self.flashcards,
                self.mcqs,
                self.revision_points,
            ]
        )
        if not has_content:
            raise ValueError("study_material must not be empty")
        return self


class EmailRequest(BaseModel):
    email: EmailStr
    study_material: StudyMaterial


class EmailResponse(BaseModel):
    success: bool
    message: str
