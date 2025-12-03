# Repository Separation Scripts

These scripts automate the process of separating the open-source codebase from private production deployment.

## Prerequisites

- Git Bash (Windows) or Bash shell (Linux/Mac)
- GitHub CLI (`gh`) installed and authenticated
- Git configured with your credentials

## Scripts Overview

### 1. prepare_public_repo.sh

**Purpose:** Clean up this public repository for open-source release

**What it does:**
- Backs up `docker-compose.yml` and `deploy_instructions.txt`
- Updates `.gitignore` to prevent committing private files
- Removes production files from git tracking
- Updates README.md and CLAUDE.md (replaces production URLs with localhost)
- Commits and pushes changes

**Usage:**

```bash
bash scripts/prepare_public_repo.sh
```

**When to run:** Once, before creating the private repository

### 2. create_private_repo.sh

**Purpose:** Create new private repository with production configs

**What it does:**
- Creates private `tamil-panchang` repo on GitHub
- Copies entire codebase to `../tamil-panchang`
- Restores production files from backup
- Initializes git and pushes to private repo
- Sets up `public` remote for syncing

**Usage:**

```bash
bash scripts/create_private_repo.sh
```

**When to run:** Once, after preparing the public repository

### 3. sync_from_public.sh

**Purpose:** Sync code changes from public to private repo

**What it does:**
- Fetches latest from public repo
- Merges changes into private repo
- Pushes to private repo (triggers Dokploy deployment)

**Usage:**

```bash
cd ../tamil-panchang
bash scripts/sync_from_public.sh
```

**When to run:** After merging PRs or updates in public repo

### 4. sync_to_public.sh

**Purpose:** Sync changes from private to public repo (optional)

**What it does:**
- Cherry-picks latest commit from private repo
- Removes any accidentally included production files
- Pushes to public repo

**Usage:**

```bash
cd ../tamil-panchang
bash scripts/sync_to_public.sh
```

**When to run:** When developing in private repo first (rare)

## Installation Steps

### Step 1: Prepare Public Repository

```bash
cd d:\tamil-panchang-api
bash scripts/prepare_public_repo.sh
```

This will:
- Remove production configs from git
- Update documentation
- Push changes to GitHub

### Step 2: Create Private Repository

```bash
bash scripts/create_private_repo.sh
```

This will:
- Create `tamil-panchang` private repo on GitHub
- Copy all files to `../tamil-panchang`
- Push to private repo

### Step 3: Configure Dokploy

**Manual step via Dokploy UI:**

1. Open Dokploy on your VPS
2. Update project settings:
   - Repository: `karthiknitt/tamil-panchang` (private)
   - Branch: `main`
   - Compose file: `docker-compose.yml`
3. Add GitHub deploy key or token
4. Test deployment

### Step 4: Regular Sync Workflow

**After updating public repo:**

```bash
cd d:\tamil-panchang
bash scripts/sync_from_public.sh
```

Dokploy will auto-deploy the changes.

## Script Compatibility

These scripts are compatible with:
- **Windows:** Git Bash, WSL
- **Linux:** Bash shell
- **Mac:** Bash shell

## Troubleshooting

### "gh: command not found"

Install GitHub CLI:

```bash
# Windows (winget)
winget install GitHub.cli

# Or download from https://cli.github.com/
```

### "Permission denied"

Make scripts executable:

```bash
chmod +x scripts/*.sh
```

### Merge conflicts during sync

```bash
# Abort merge
git merge --abort

# Manually resolve
git fetch public
git merge public/main
# Fix conflicts, then:
git add .
git commit
git push origin main
```

## Safety Features

All scripts include:
- **Backup creation** before destructive operations
- **Confirmation prompts** for important decisions
- **Error checking** (exits on failure)
- **Status reporting** at each step

## Files Affected

### Public Repo (tamil-panchang-api)

**Removed:**
- `docker-compose.yml` (production)
- `deploy_instructions.txt`

**Modified:**
- `.gitignore` (add private file exclusions)
- `README.md` (localhost URLs)
- `CLAUDE.md` (localhost URLs)

**Unchanged:**
- All source code
- `docker-compose.standalone.yml`

### Private Repo (tamil-panchang)

**Kept:**
- All source code
- `docker-compose.yml` (production)
- `deploy_instructions.txt`
- All other files

## Quick Reference

```bash
# Initial setup
bash scripts/prepare_public_repo.sh
bash scripts/create_private_repo.sh

# Regular sync (public → private)
cd ../tamil-panchang
bash scripts/sync_from_public.sh

# Rare sync (private → public)
bash scripts/sync_to_public.sh
```

## Support

For issues or questions, refer to:
- Main plan: [REPOSITORY_SEPARATION_PLAN.md](../REPOSITORY_SEPARATION_PLAN.md)
- Claude plan: `C:\Users\karth\.claude\plans\smooth-gathering-bear.md`
