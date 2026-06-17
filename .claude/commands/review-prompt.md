---
name: review-prompt
description: Reviews a prompt before executing it — checks clarity, scope, architecture, and safety against the cAIpherPass plan. Use before any non-trivial task.
argument-hint: <your instruction to review>
---

# /review-prompt

The user's instruction to review is: **$ARGUMENTS**

Review this instruction before executing anything. Never skip this review.

## How to use
The user types: `/review-prompt <their instruction>`
You review it, give feedback, then ask whether to proceed.

Context for this project lives in `CLAUDE.md` (how we work) and `plan.txt` (what we
build). Judge the instruction against those — not against generic assumptions.

---

## Step 1 — Run through this checklist

Check the instruction against every item below and note any failures:

**Clarity**
- [ ] Is it clear which file or layer changes? (`core/`, `gui/`, `ai/`, `data/`)
- [ ] Is the expected result described? (what should happen after the change)
- [ ] Any undefined words like "fix it", "make it better", "improve", "secure it"?

**Scope**
- [ ] Does it ask for ONE thing, or several bundled together?
- [ ] Is it small enough to test in one step?

**Architecture (cAIpherPass rules)**
- [ ] Does it respect the locked stack? (SQLite/`sqlite3`, `cryptography` Fernet+PBKDF2,
      CustomTkinter, `secrets`, scikit-learn for Phase 2)
- [ ] Does it introduce a dependency not in the plan? (flag it, don't add silently)
- [ ] Does it respect the layer split? (generation/encryption/database in `core/`,
      UI in `gui/`, ML in `ai/`)
- [ ] Does it skip the build order? (e.g. GUI work before the core function exists)

**Safety (password manager — treat seriously)**
- [ ] Destructive actions? (delete, drop table, reset, force push, wiping `vault.db`)
- [ ] Does it risk storing the **master password** in any reversible form? (must never happen)
- [ ] Does it use `secrets` for anything security-relevant — never `random`?
- [ ] Does only **encrypted** data reach the database?
- [ ] Could it commit secrets or the vault to git? (must stay git-ignored)
- [ ] Does it change something other parts depend on? (function signatures, DB schema, key derivation)

---

## Step 2 — Score it

Give a score from 1 to 5:
- **5** — clear, specific, one thing, safe to proceed immediately
- **4** — mostly good, minor clarification needed
- **3** — vague or too broad, needs improvement before proceeding
- **2** — multiple things bundled, or missing important context
- **1** — too vague to act on safely, or potentially destructive / a security risk

---

## Step 3 — Give feedback

Format your response like this:

---
**Prompt Review**

**Score:** X/5

**Issues found:**
- [list each problem clearly, or say "None" if clean]

**Suggested improved prompt:**
> [rewrite the instruction as a clear, specific, single-task prompt]

**Verdict:** [one of: ✅ Ready to proceed | ⚠️ Needs minor clarification | ❌ Please refine before proceeding]

---

Then ask: "Should I proceed with the improved prompt, use your original, or would you like to refine it further?"

---

## Examples of bad → good prompts (cAIpherPass)

| Bad | Good |
|---|---|
| "Make the generator" | "In `core/generator.py`, write `generate_password(length, use_upper, use_digits, use_symbols)` using the `secrets` module. Return a string of that length built only from the enabled character sets." |
| "Add encryption" | "In `core/encryption.py`, add `derive_key(master_password, salt)` that uses PBKDF2-HMAC-SHA256 to derive a 32-byte Fernet key. Don't store the master password — just return the key." |
| "Set up the database" | "In `core/database.py`, create the `vault` table with columns: id, service_name, username, encrypted_password, created_at, tags. Add an `init_db()` that creates it if missing." |
| "Fix the UI and add search and encrypt everything" | Pick ONE: "In `gui/app.py`, add a search box that filters the entry list by `service_name` as the user types." |
| "Store the master password so login is faster" | ❌ Never store the master password. Instead: "At Step 2, design master-password verification (encrypted canary vs. password hash) — don't persist the password itself." |
