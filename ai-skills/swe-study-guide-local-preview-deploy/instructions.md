# swe-study-guide Local Preview Deploy

Use this skill when the user wants the current repository state visible in the local study site, usually at `http://127.0.0.1:8766/`.

If the user asks about the Hetzner VPS or production deployment, use `swe-study-guide-deploy` instead. Production must run `origin/main`, not a fix or feature branch.

Read first:
- `AGENTS.md`
- `README.md`
- `docs/INDEX.md`
- `serve.py`

Default behavior:
- treat "deploy" here as a local preview refresh, not a GitHub release
- prefer reusing port `8766` when the user names that URL
- verify both the content API and the browser-facing site after restarting
- leave the broader production-deploy workflow to `swe-study-guide-deploy`

## Use this skill for

- "Deploy this locally"
- "Make this visible at `127.0.0.1:8766`"
- "Refresh the study site"
- "The new content files exist but the sidebar doesn't show them"

## Workflow

### 1. Check whether a local server is already listening

Run:

```bash
lsof -nP -iTCP:8766 -sTCP:LISTEN || true
```

If another `serve.py` process is already listening on the target port, assume it may have a stale in-memory index. `serve.py` builds the content index only at startup.

### 2. Verify whether the running server is stale

Check the content API first:

```bash
python3 - <<'PY'
import json, urllib.request
payload = json.load(urllib.request.urlopen('http://127.0.0.1:8766/api/content'))
print([tech["dir"] for tech in payload["technologies"]])
PY
```

If the expected technology or topic is missing from `/api/content` but the raw file is reachable under `/content/...`, the server is stale and needs a restart.

### 3. Restart `serve.py` on the requested port

If an old process is listening, stop it first. Then start the server from the repository root:

```bash
python3 -u serve.py --port 8766
```

Use a foreground session when you need reliable verification right away. Detached starts can hide startup failures.

If you must run it in the background, capture logs somewhere explicit and confirm the process is still listening before telling the user it worked.

### 4. Verify the refreshed content index

Check the API:

```bash
python3 - <<'PY'
import json, urllib.request
payload = json.load(urllib.request.urlopen('http://127.0.0.1:8766/api/content'))
for tech in payload["technologies"]:
    if tech["dir"] == "06_Backend_API":
        print(json.dumps(tech, indent=2))
        break
PY
```

Also verify a representative content file:

```bash
curl -sSf http://127.0.0.1:8766/content/06_Backend_API/01_API_Design_and_Contracts/concepts.md | head
```

### 5. Verify the browser-facing site

Load:

```text
http://127.0.0.1:8766/
```

Check that:
- the page loads
- the new technology appears in the sidebar
- the expected topics are listed underneath it

If browser automation is available, use it. A missing `favicon.ico` 404 is harmless and should not be treated as a deployment failure.

## Common failure modes

- **Port already in use** — another local preview is still running.
- **Content file loads but sidebar is stale** — the old `serve.py` process was not restarted after content changes.
- **Detached restart silently dies** — rerun `python3 -u serve.py --port <port>` in the foreground to see the real startup error.
- **`/api/content` works on one port but not another** — the user may be looking at an older process bound to a different port.

## Output expectations

- The requested local URL serves the current checkout.
- The relevant technology or topic appears in `/api/content`.
- The user gets a short summary of what process was restarted, which port is serving, and what was verified.
