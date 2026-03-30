from typing import Optional
from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    account_name: str = Field(..., description="The name of the account to look up")


class StakeholderResponse(BaseModel):
    csm_name: Optional[str]
    csm_email: Optional[str]
    exec_sponsor_name: Optional[str]
    exec_sponsor_email: Optional[str]


class ActionItemRequest(BaseModel):
    account_name: str = Field(..., description="The name of the account to create the action item for")
    owner: str = Field(..., min_length=1, max_length=255, description="The person responsible for this action item")
    action: str = Field(..., min_length=1, max_length=1000, description="Description of the action item")


class ActionItemResponse(BaseModel):
    id: int
    account: str
    owner: str
    action: str
    created_at: str
