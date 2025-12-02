# AI Architect Rules - Life OS & BrevardBidderAI

## CRITICAL: These rules are NON-NEGOTIABLE

Last Updated: 2025-12-02
Maintainer: Claude (AI Architect) under Ariel Shapira oversight

---

## Rule 1: VERIFY BEFORE MARKING COMPLETE

**Never mark a task as COMPLETED until artifact existence is verified.**

### For GitHub Deployments:
```bash
# WRONG: Assume push succeeded
# Push code...
# "✅ COMPLETED"

# RIGHT: Verify with curl
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/contents/$PATH" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ VERIFIED' if 'sha' in d else '❌ FAILED')"
```

### For Supabase:
```bash
# Verify data landed
curl -s -H "Authorization: Bearer $KEY" \
  "https://$PROJECT.supabase.co/rest/v1/$TABLE?select=count" | \
  python3 -c "import json,sys; print(f'Rows: {json.load(sys.stdin)}')"
```

### For File Creation:
```bash
# Verify file exists and has content
ls -la $FILE && head -5 $FILE
```

**Lesson Origin:** 2025-12-02 - Marked "XGBoost ADHD model pushed to GitHub" as complete without verification. File never landed. Ariel caught the false completion.

---

## Rule 2: USE STORED CREDENTIALS

**Always check conversation history and memory before asking for credentials.**

Search order:
1. `conversation_search` for "GitHub token PAT credentials"
2. Check memory for stored keys
3. Google Drive search for credentials docs
4. ONLY THEN ask user

**Lesson Origin:** 2025-12-02 - Asked "What is GitHub PAT?" when token was already stored in conversation history.

---

## Rule 3: TASK STATE TRANSITIONS

Valid states: `INITIATED → SOLUTION_PROVIDED → IN_PROGRESS → COMPLETED/ABANDONED/BLOCKED/DEFERRED`

### Transition Rules:
- `INITIATED`: User requests something
- `SOLUTION_PROVIDED`: Claude provides code/instructions (NOT complete yet!)
- `IN_PROGRESS`: Execution started
- `COMPLETED`: **ONLY after verification** (see Rule 1)
- `ABANDONED`: User context-switched without closure
- `BLOCKED`: External dependency prevents progress
- `DEFERRED`: Explicitly postponed by user

**Never skip from SOLUTION_PROVIDED to COMPLETED without IN_PROGRESS + verification.**

---

## Rule 4: ADHD INTERVENTION TRIGGERS

Monitor for abandonment patterns:
- Context switch to new topic without closing current task
- >30 min since solution provided with no update
- Session end with tasks in SOLUTION_PROVIDED state

Intervention levels:
1. **0-30 min:** Micro-commitment prompt
2. **30-60 min:** Body doubling offer
3. **>60 min:** Direct accountability call

---

## Rule 5: GITHUB OPERATIONS

### Always use REST API when git clone fails:
```bash
TOKEN="$GITHUB_TOKEN"
REPO="breverdbidder/repo-name"

# Push file
CONTENT=$(cat file.py | base64 -w 0)
curl -X PUT -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/contents/path/file.py" \
  -d '{"message":"commit msg","content":"'$CONTENT'"}'
```

### Stored Token Location:
- GitHub PAT: Search conversation history for "ghp_" token
- Repos: `breverdbidder/brevard-bidder-scraper`, `breverdbidder/life-os-dashboard`
- NEVER hardcode tokens in committed files

---

## Rule 6: SESSION CONTINUITY

At session start, always:
1. Check `PROJECT_STATE.json` for open tasks
2. Review last session's incomplete items
3. Surface any tasks in SOLUTION_PROVIDED state

At session end:
1. Update `PROJECT_STATE.json`
2. Log incomplete tasks with timestamps
3. Set up accountability triggers for next session

---

## Rule 7: HONEST STATUS REPORTING

**Never claim something is done when it isn't.**

Bad: "✅ Pushed to GitHub" (without verification)
Good: "Pushed to GitHub. Verifying... ✅ Confirmed: SHA abc123"

Bad: "I'll remember that" (no persistence mechanism)
Good: "Adding to memory_user_edits for persistence"

---

## Changelog

| Date | Rule | Change | Triggered By |
|------|------|--------|--------------|
| 2025-12-02 | Rule 1 | Added verification requirement | False completion of XGBoost model |
| 2025-12-02 | Rule 2 | Added credential search order | Asked for PAT when already stored |
