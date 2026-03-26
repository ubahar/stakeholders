import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Optional[Client] = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _client = create_client(url, key)
    return _client


def lookup_account(account_name: str) -> Optional[dict]:
    client = get_client()
    result = (
        client.table("accounts")
        .select("csm_name, csm_email, exec_sponsor_name, exec_sponsor_email")
        .eq("account_name", account_name)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]
    return None
