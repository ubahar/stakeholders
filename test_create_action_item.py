"""
Unit tests for the create_action_item Opal tool.

Security risks covered:
- Unauthorized inserts: handled by Opal SDK bearer auth (not tested here — SDK responsibility)
- Account spoofing: unknown account_name is rejected before any insert
- Unbounded input: Pydantic max_length validation fires before DB is touched
- FK violation / DB errors: exception is caught and returned as a clean error dict
"""

from unittest.mock import MagicMock, patch
import pytest
from pydantic import ValidationError

from models import ActionItemRequest
from db import get_account_id, create_action_item


# ---------------------------------------------------------------------------
# Model validation tests
# ---------------------------------------------------------------------------

def test_action_item_request_valid():
    req = ActionItemRequest(account_name="Acme Corp", owner="Jane Doe", action="Follow up on renewal")
    assert req.account_name == "Acme Corp"
    assert req.owner == "Jane Doe"
    assert req.action == "Follow up on renewal"


def test_action_item_request_action_too_long():
    with pytest.raises(ValidationError):
        ActionItemRequest(account_name="Acme Corp", owner="Jane Doe", action="x" * 1001)


def test_action_item_request_owner_empty():
    with pytest.raises(ValidationError):
        ActionItemRequest(account_name="Acme Corp", owner="", action="Follow up on renewal")


def test_action_item_request_owner_too_long():
    with pytest.raises(ValidationError):
        ActionItemRequest(account_name="Acme Corp", owner="x" * 256, action="Follow up on renewal")


# ---------------------------------------------------------------------------
# DB function tests
# ---------------------------------------------------------------------------

@patch("db.get_client")
def test_get_account_id_found(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": "abc-123-uuid"}
    ]
    result = get_account_id("Acme Corp")
    assert result == "abc-123-uuid"


@patch("db.get_client")
def test_get_account_id_not_found(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
    result = get_account_id("Unknown Corp")
    assert result is None


@patch("db.get_client")
def test_create_action_item_success(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        {
            "id": 42,
            "account": "abc-123-uuid",
            "owner": "Jane Doe",
            "action": "Follow up on renewal",
            "created_at": "2026-03-26T10:00:00+00:00",
        }
    ]
    result = create_action_item("abc-123-uuid", "Jane Doe", "Follow up on renewal")
    assert result["id"] == 42
    assert result["owner"] == "Jane Doe"
    assert result["action"] == "Follow up on renewal"
    assert "created_at" in result


# ---------------------------------------------------------------------------
# Tool handler integration tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@patch("main.get_account_id", return_value=None)
async def test_tool_unknown_account(mock_get_account_id):
    from main import create_action_item_tool
    params = ActionItemRequest(account_name="Ghost Corp", owner="Jane Doe", action="Follow up")
    result = await create_action_item_tool(params)
    assert "error" in result
    assert "Ghost Corp" in result["error"]
    mock_get_account_id.assert_called_once_with("Ghost Corp")


@pytest.mark.asyncio
@patch("main.create_action_item", side_effect=Exception("FK violation"))
@patch("main.get_account_id", return_value="abc-123-uuid")
async def test_tool_db_error_returns_clean_error(mock_get_account_id, mock_create):
    from main import create_action_item_tool
    params = ActionItemRequest(account_name="Acme Corp", owner="Jane Doe", action="Follow up")
    result = await create_action_item_tool(params)
    assert "error" in result
    assert "FK violation" in result["error"]


@pytest.mark.asyncio
@patch("main.create_action_item", return_value={
    "id": 1,
    "account": "abc-123-uuid",
    "owner": "Jane Doe",
    "action": "Follow up on renewal",
    "created_at": "2026-03-26T10:00:00+00:00",
})
@patch("main.get_account_id", return_value="abc-123-uuid")
async def test_tool_happy_path(mock_get_account_id, mock_create):
    from main import create_action_item_tool
    params = ActionItemRequest(account_name="Acme Corp", owner="Jane Doe", action="Follow up on renewal")
    result = await create_action_item_tool(params)
    assert result["id"] == 1
    assert result["owner"] == "Jane Doe"
    assert "created_at" in result
