from pydantic import BaseModel

class ProjectionBase(BaseModel):
    ticker: str
    move_prediction: str
    action: str
    logic: str

class ProjectionCreate(ProjectionBase):
    pass

class ProjectionResponse(ProjectionBase):
    id: int

    class Config:
        from_attributes = True
