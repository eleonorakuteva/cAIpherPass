---
description: Delete the vault database to reset to first-time setup
---

# delete-the-db

Deletes the `data/vault.db` file to reset the app to first-time setup mode. Useful for testing the master password setup flow repeatedly.

## What it does

- Removes `data/vault.db` if it exists
- App will show the "Set Master Password" setup screen on next launch
- All stored vault data is lost (intentional for testing)

## Usage

```
/delete-the-db
```

Or from the terminal:

```powershell
Remove-Item -Path "C:\Users\eleon\Desktop\cAIpherPass\data\vault.db" -Force
```

## When to use

- After setting up a master password, to test the setup flow again
- Before testing the login screen after setup
- To reset the app to a clean state for testing

## Example workflow

1. Run the app and set a master password
2. Run `/delete-the-db`
3. Run the app again → sees the setup screen (fresh start)
