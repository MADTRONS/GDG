"""Counselor schemas for API responses."""
from pydantic import BaseModel, UUID4, ConfigDict
from typing import List


class CounselorCategoryResponse(BaseModel):
    """Response schema for counselor category."""
    id: UUID4
    name: str
    description: str
    icon_name: str

    model_config = ConfigDict(from_attributes=True)


class CounselorCategoriesResponse(BaseModel):
    """Response schema for list of counselor categories."""
    categories: List[CounselorCategoryResponse]
    total: int
