# Stakeholder Lookup — Optimizely Opal Custom Tool

Looks up the CSM and Executive Sponsor for a given account name from a Supabase database.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with your values
```

## Supabase Table

Create this table in your Supabase project (SQL editor):

```sql
CREATE TABLE accounts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  account_name text UNIQUE NOT NULL,
  csm_name text,
  csm_email text,
  exec_sponsor_name text,
  exec_sponsor_email text
);
```

## Run Locally

```bash
python3 -m uvicorn main:app --reload
```

- Discovery manifest: `GET http://localhost:8000/discovery`
- Execute: `POST http://localhost:8000/execute`
- Interactive docs: `http://localhost:8000/docs`

## Test the Execute Endpoint

```bash
curl -X POST https://your-ngrok-url/execute \
  -H "Authorization: Bearer your-secret-bearer-token" \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{"account_name": "Acme Corp"}'
```

Expected response:
```json
{
  "csm_name": "Jane Doe",
  "csm_email": "jane@example.com",
  "exec_sponsor_name": "John Smith",
  "exec_sponsor_email": "john@example.com"
}
```

## Expose Locally via ngrok

To register the tool with Optimizely Opal without a full deployment, use ngrok to expose your local server.

**Install ngrok:**
```bash
brew install ngrok
```

Or download from https://ngrok.com/download and add to PATH.

**Authenticate (one-time setup):**
```bash
ngrok config add-authtoken <your-ngrok-token>
```
Get your token at https://dashboard.ngrok.com/get-started/your-authtoken

**Start the tunnel** (while the server is running on port 8000):
```bash
ngrok http 8000
```

ngrok will output a public URL like `https://abc123.ngrok-free.app`. Update your `.env`:
```
TOOL_BASE_URL=https://abc123.ngrok-free.app
```

Then restart the server so the discovery manifest reflects the new URL.

## Register in Optimizely Opal

1. Start the local server and ngrok tunnel (see above)
2. In Opal, register the tool using: `https://abc123.ngrok-free.app/discovery`
3. Use `OPTI_SECRET_TOKEN` as the bearer token credential in Opal

> For production, replace ngrok with a permanent deployment (e.g. Railway, Render, Fly.io) and set `TOOL_BASE_URL` accordingly.
