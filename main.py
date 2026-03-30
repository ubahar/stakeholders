import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from opal_tools_sdk import ToolsService, tool

from models import ExecuteRequest, ActionItemRequest
from db import lookup_account, get_account_id, create_action_item

load_dotenv()

app = FastAPI(title="Stakeholder Lookup Tool")
tools_service = ToolsService(app)


@app.middleware("http")
async def add_ngrok_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


@tool("stakeholder_lookup", "Look up the CSM and Executive Sponsor for a given account")
async def stakeholder_lookup(parameters: ExecuteRequest):
    row = lookup_account(parameters.account_name)
    if row is None:
        return {"error": f"Account '{parameters.account_name}' not found"}
    return row


@tool("create_action_item", "Create an action item for a given account")
async def create_action_item_tool(parameters: ActionItemRequest):
    account_id = get_account_id(parameters.account_name)
    if account_id is None:
        return {"error": f"Account '{parameters.account_name}' not found"}
    try:
        result = create_action_item(account_id, parameters.owner, parameters.action)
        return result
    except Exception as e:
        return {"error": f"Failed to create action item: {str(e)}"}
