from typing import Optional
from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    account_name: str = Field(..., description="The name of the account to look up")


class StakeholderResponse(BaseModel):
    csm_name: Optional[str]
    csm_email: Optional[str]
    exec_sponsor_name: Optional[str]
    exec_sponsor_email: Optional[str]
