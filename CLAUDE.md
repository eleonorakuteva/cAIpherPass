# CLAUDE.md — cAIpherPass

This file is my guide for working on this project. I read it at the start of each session.
If anything here goes stale, update it.

## What this project is

**cAIpherPass** — a local desktop password manager built in Python, for an
**AI Assistant Development course**. It is a learning project first, a product second.

Core features:
- Cryptographically secure password generation (custom length + character sets)
- Local **encrypted** storage (master password never stored)
- Search through saved entries
- An AI password-strength classifier (rule-based first, ML later)

This file is the single source of truth for the project — both *how we work* and
*what we build*. The design rationale (the *why* behind each tool, schema notes,
AI phases) lives in the "Design / app logic" section below.

## Who I'm working with

- A student learning AI-assisted development tools (Copilot, Claude Code, etc.).
- Background: **Python and SQL**. New to: cryptography, CustomTkinter, ML/scikit-learn.
- Platform: **Windows 11**, shell is **PowerShell**, Python **3.14**, git available.

## How to work with me (IMPORTANT)

**Teach as we go.** This is the agreed working style:
- Explain the *why* before writing code. Introduce one concept at a time.
- Keep changes **small and reviewable** — prefer a working slice over a big dump.
- After writing code, briefly walk through what it does and check understanding.
- When there's a meaningful design choice, surface the trade-off and let the user decide.
- Don't silently introduce libraries or patterns beyond the plan without flagging them.
- It's fine to be a tutor: point out *standard practice* and *security pitfalls* as we hit them.

## Tech stack (locked for this project)

| Area        | Tool                                   | Notes |
|-------------|----------------------------------------|-------|
| GUI         | CustomTkinter                          | `pip install customtkinter` |
| Database    | SQLite via built-in `sqlite3`          | file at `data/vault.db` (generated at runtime) |
| Encryption  | `cryptography` — Fernet + PBKDF2       | `pip install cryptography` |
| Generation  | built-in `secrets`                     | NOT `random` — must be crypto-secure |
| AI (Phase 1)| rule-based scorer                      | no deps |
| AI (Phase 2)| scikit-learn                           | `pip install scikit-learn` |
| Packaging   | PyInstaller (later)                    | `pip install pyinstaller` |

## Build order

1. Password generator core (`secrets`)
2. Encryption layer (master password → PBKDF2 → Fernet key)
3. SQLite schema + CRUD (save / load / delete)
4. CustomTkinter GUI (generate, save, search)
5. Rule-based strength scorer (Phase 1 AI)
6. ML strength classifier with scikit-learn (Phase 2 AI)
7. Polish + PyInstaller packaging

Work top-down; don't jump ahead unless the user asks.

## Design / app logic (the *why*)

The reasoning behind each piece of the stack, plus the details we'll need when we
reach each step.

**GUI — CustomTkinter.** Modern-looking, pure Python, easy to learn. A good
foundation before heavier frameworks later.

**Database — SQLite (`sqlite3`).** Local file-based, no server needed; standard SQL
skills that transfer everywhere. Planned `vault` table columns:
- `id`
- `service_name` (e.g. "Gmail", "GitHub")
- `username`
- `encrypted_password`
- `created_at`
- `valid_to` — *open question (decide at Step 3):* a password-expiry date? Keep it
  or drop it when we build the schema.
- `tags` (optional, for search)

**Encryption — `cryptography` (Fernet + PBKDF2).** Flow:
1. User sets a master password on first launch.
2. Master password is run through PBKDF2 to derive an encryption key.
3. That key is used by Fernet to encrypt/decrypt passwords.
4. The master password itself is **never stored**.

**Password generation — `secrets`.** Cryptographically secure, unlike `random`. Full
control over length and character sets. Options to expose in the GUI:
- Length (slider or input)
- Include uppercase letters
- Include digits
- Include special symbols (`!@#$%^&*` etc.)

**AI strength classifier — two phases:**
- *Phase 1 — rule-based (build first).* Score on length, has-uppercase, has-digits,
  has-symbols, and an entropy estimate. Output a Low / Medium / Hard label. No ML,
  fast to implement.
- *Phase 2 — ML (scikit-learn).* Train a classifier on labelled password data to
  predict strength; replaces or augments the rule-based scorer once Phase 1 works.

**Packaging — PyInstaller (future).** Bundle the app into a standalone `.exe` for
Windows.

## Security principles (non-negotiable for a password manager)

- The **master password is never stored** anywhere, in any form we can reverse.
- Derive the encryption key from the master password with **PBKDF2** (store the salt only).
- Only the **encrypted** password ever touches the database.
- Use `secrets`, never `random`, for anything security-relevant.
- **Open design decision (revisit at Step 2):** how to verify the master password is
  correct on login without storing it. Candidate approaches: an encrypted "canary"
  token decrypted with the derived key, or a separate password hash. *Decide together
  when we reach the encryption layer.*

## Environment / conventions

- Windows + PowerShell. Use PowerShell syntax in commands (`$env:VAR`, not `$VAR`).
- `data/vault.db` and any local secrets must be **git-ignored** (no `.gitignore` yet —
  create one before the DB is first generated).
- Keep a `requirements.txt` in sync as we add dependencies.

## Status

- [x] Project introduced, plan reviewed, CLAUDE.md created.
- [x] Step 1: Password generator (`core/generator.py`) — complete.
- [x] Step 2: Encryption layer (`core/encryption.py`) — complete.
- [x] Step 3: Database layer (`database/database.py`, `database/schemas.py`) — complete.
  - SQLite schema with vault + metadata tables
  - Salt management (generated on first launch, retrieved on login)
  - CRUD operations with full input validation
  - Data integrity guaranteed (bad data rejected before SQL)
- [x] Step 4: GUI (CustomTkinter) — complete.
  - Login/setup screen (`gui/app.py` → `LoginApp`): first-launch master-password
    setup with confirm + 8-char minimum; verify on later launches.
  - Main vault (`MainApp`) with two tabs:
    - Add New Entry — entry form (service, username, password, tags) + password
      generator card (per-type count sliders, live total length), Generate / Copy / Save.
    - Vault — searchable table (live debounced search, decrypt-once cache),
      reveal / copy / delete per row.
- [x] Step 5: Rule-based strength scorer (Phase 1 AI) — complete.
  - `ai/strength.py`: entropy-based scorer (length × log2(pool)) with capping
    penalties (too-short → Weak, single-type → Medium) and a Weak/Medium/Strong
    label + reason hint. No ML — hand-written rules, the Phase 2 baseline.
  - `test_strength.py`: 9 passing checks incl. regressions (single-type cap must
    not raise a weak password; must lower a long single-type one).
  - GUI: live colour-coded strength badge in the Add New Entry tab; removed the
    lowercase slider's minimum=1 floor so single-type generation scores correctly.
- [ ] Step 6: ML strength classifier (scikit-learn, Phase 2 AI) — next.
