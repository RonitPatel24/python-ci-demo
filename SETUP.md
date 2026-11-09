# CI/CD Pipeline Setup: GitHub → ngrok → Jenkins (Docker) → Webex

```
git push ──► GitHub ──webhook──► ngrok ──► Jenkins (Docker :8080) ──► python unittest ──► Webex bot ──► your space
```

---

## 1. GitHub repo

```bash
cd python-ci-demo
git init -b main
git add .
git commit -m "Initial commit: calculator + tests + Jenkinsfile"
# Create an empty public repo named python-ci-demo on github.com first, then:
git remote add origin https://github.com/<your-username>/python-ci-demo.git
git push -u origin main
```

> Keep the repo **public** — that way Jenkins can clone it without credentials.

---

## 2. Jenkins in Docker

The `jenkins/Dockerfile` adds `python3`, `git` and `curl` to the official image (the stock image has no Python, so tests would fail).

```bash
cd jenkins
docker compose up -d --build
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open http://localhost:8080 → paste the password → **Install suggested plugins** → create an admin user.

Verify Python is inside the container:

```bash
docker exec jenkins python3 --version
```

### Plugins
**Manage Jenkins → Plugins → Available**, install (most come with "suggested"):

| Plugin | Why |
|---|---|
| Git, Pipeline | checkout + Jenkinsfile |
| **GitHub** | provides `githubPush()` and the `/github-webhook/` endpoint |
| **Timestamper** | `timestamps()` in the Jenkinsfile |
| Credentials Binding | `withCredentials` for the Webex secrets |

---

## 3. ngrok

1. Sign up at ngrok.com, copy your authtoken.
2. ```bash
   ngrok config add-authtoken <TOKEN>
   ngrok http 8080
   ```
3. Copy the `https://xxxx.ngrok-free.app` forwarding URL.
4. Keep this terminal visible — its request log is what earns the **20 points** for "ngrok showing the incoming webhook". The web inspector at http://127.0.0.1:4040 shows full payloads too.

Optional: in Jenkins **Manage Jenkins → System → Jenkins URL**, set it to the ngrok URL so the "Console:" link in Webex works from anywhere.

> Free ngrok URLs change every restart. If you restart ngrok, update the GitHub webhook URL.

---

## 4. GitHub webhook

Repo → **Settings → Webhooks → Add webhook**

| Field | Value |
|---|---|
| Payload URL | `https://xxxx.ngrok-free.app/github-webhook/` ← **trailing slash required** |
| Content type | `application/json` |
| Events | Just the push event |

Save. GitHub sends a `ping`; you should see `POST /github-webhook/ 200` in the ngrok terminal and a green check under **Recent Deliveries**.

---

## 5. Webex bot

1. Go to https://developer.webex.com → log in → **My Webex Apps → Create a New App → Create a Bot**.
2. Name/username/icon → **Add Bot**. **Copy the Bot Access Token now** (shown once).
3. In the Webex app, create a space (e.g. "Jenkins Builds") and **add the bot by its email** (`yourbot@webex.bot`).
4. Get the room ID:
   ```bash
   curl -s -H "Authorization: Bearer <BOT_TOKEN>" https://webexapis.com/v1/rooms
   ```
   Copy the `id` of your space.
5. Test it:
   ```bash
   curl -X POST https://webexapis.com/v1/messages \
     -H "Authorization: Bearer <BOT_TOKEN>" -H "Content-Type: application/json" \
     -d '{"roomId":"<ROOM_ID>","text":"Hello from the bot"}'
   ```

---

## 6. Jenkins credentials

**Manage Jenkins → Credentials → System → Global credentials → Add Credentials**, kind **Secret text**, twice:

| ID (must match exactly) | Secret |
|---|---|
| `webex-bot-token` | Bot access token |
| `webex-room-id` | Room ID |

---

## 7. Pipeline job

**New Item** → name `python-ci-demo` → **Pipeline** → OK.

- **Triggers:** tick **GitHub hook trigger for GITScm polling**
- **Pipeline:**
  - Definition: *Pipeline script from SCM*
  - SCM: Git → Repository URL: `https://github.com/<you>/python-ci-demo.git`
  - Branch Specifier: `*/main`
  - Script Path: `Jenkinsfile`
- Save → **Build Now** once (registers the webhook trigger and confirms everything works; you should get a Webex message).

---

## 8. Test the full loop

```bash
# make a small visible change
echo '    print("3 * 4 =", multiply(3, 4))' >> calculator.py   # or edit by hand
git commit -am "Demo: trigger pipeline from commit"
git push
```

Expected: ngrok logs `POST /github-webhook/ 200 OK` → Jenkins build #N starts on its own → console shows 6 tests `ok` and `Finished: SUCCESS` → Webex gets "✅ BUILD SUCCESS".

---

## Recording checklist (80 pts)

Arrange windows before hitting record: **editor/terminal**, **ngrok terminal**, **browser tabs** (GitHub repo, Jenkins job, Webex space).

1. **Edit + commit** – show the change in the editor, run `git commit` + `git push` in the terminal.
2. **GitHub (10)** – refresh the repo; point at your commit message with the "now" / "1 minute ago" timestamp.
3. **ngrok (20)** – switch to the ngrok terminal; show the new `POST /github-webhook/ 200 OK` line (optionally open :4040 to show the push payload).
4. **Jenkins auto-trigger (20)** – show the new build in Build History; open it — the cause line reads "Started by GitHub push by <you>".
5. **Console output (20)** – scroll the Console Output through all 6 `... ok` lines, `Ran 6 tests`, `OK`, and `Finished: SUCCESS`.
6. **Webex (10)** – show the bot's ✅ message with the matching commit hash.

Narrate briefly or add captions; keep it under ~5 minutes.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Webhook delivery 404 / 403 | Missing trailing slash on `/github-webhook/`, or the GitHub plugin isn't installed |
| Webhook 200 but no build | Didn't tick "GitHub hook trigger…", or never ran **Build Now** once; repo URL in the job must match the repo that sent the hook |
| `python3: not found` | Jenkins wasn't built from the custom Dockerfile — rerun `docker compose up -d --build` |
| `No such DSL method 'timestamps'` | Install the Timestamper plugin |
| `Could not find credentials entry with ID 'webex-bot-token'` | Credential IDs must match exactly |
| Webex API HTTP status 401 | Bad/expired bot token |
| Webex 404 | Bot isn't a member of the space, or wrong room ID |
| ngrok shows nothing | Webhook still points to an old ngrok URL |
| Browser warning page from ngrok | Only affects browsers; GitHub webhooks pass through fine |
