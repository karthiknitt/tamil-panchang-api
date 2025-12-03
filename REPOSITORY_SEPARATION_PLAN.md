# Repository Separation Plan: Open-Source and Private Deployment

## Executive Summary

**Goal:** Separate the open-source codebase from private production deployment configurations.

**Solution:** Two-repository approach
- **Private repo:** `tamil-panchang` - Production deployment with Traefik
- **Public repo:** `tamil-panchang-api` (current) - Open-source without Traefik

**Implementation:** Automated shell scripts for all major operations.

---

## Strategy

### Repository 1 (Private): tamil-panchang

- **Visibility:** Private on GitHub
- **Purpose:** Production VPS deployment via Dokploy
- **Contains:**
  - All source code
  - `docker-compose.yml` with Traefik, domain, SSL
  - `deploy_instructions.txt`
  - Production configurations

### Repository 2 (Public): tamil-panchang-api

- **Visibility:** Public on GitHub
- **Purpose:** Open-source version for community
- **Contains:**
  - All source code
  - `docker-compose.standalone.yml` only (no Traefik)
  - Generic documentation (localhost examples)
  - No domain or private configs

---

## Implementation Steps

### Phase 1: Prepare Public Repository

**Automated:** Run `scripts/prepare_public_repo.sh`

**Manual alternative:**

```bash
cd d:\tamil-panchang-api

# Backup production files
cp docker-compose.yml docker-compose.yml.backup
cp deploy_instructions.txt deploy_instructions.txt.backup

# Update .gitignore
cat >> .gitignore << 'EOF'

# Private deployment files (never commit)
docker-compose.yml
deploy_instructions.txt
.env
.env.production
.env.local
EOF

# Remove production files from git
git rm docker-compose.yml
git rm deploy_instructions.txt

# Update documentation (use sed or manual edit)
sed -i 's|https://panchang.karthikwrites.com|http://localhost:8000|g' README.md
sed -i 's|https://panchang.karthikwrites.com|http://localhost:8000|g' CLAUDE.md

# Commit and push
git add .gitignore README.md CLAUDE.md
git commit -m "Prepare repository for open-source release"
git push origin main
```

### Phase 2: Create Private Repository

**Automated:** Run `scripts/create_private_repo.sh`

**Manual alternative:**

```bash
# Create private repo on GitHub
gh repo create tamil-panchang --private \
  --description "Private production deployment for Tamil Panchang API"

# Copy codebase
cd ..
cp -r tamil-panchang-api tamil-panchang
cd tamil-panchang

# Restore production files
mv docker-compose.yml.backup docker-compose.yml
mv deploy_instructions.txt.backup deploy_instructions.txt

# Initialize git
rm -rf .git
git init
git add .
git commit -m "Initial commit for private production repository"
git remote add origin https://github.com/karthiknitt/tamil-panchang.git
git branch -M main
git push -u origin main

# Set up sync with public repo
git remote add public https://github.com/karthiknitt/tamil-panchang-api.git
git fetch public
```

### Phase 3: Configure Dokploy

**Steps:**

1. Access Dokploy UI on your VPS
2. Update repository settings:
   - Change source from `tamil-panchang-api` to `tamil-panchang`
   - Ensure GitHub access (deploy key or token)
   - Branch: `main`
   - Compose file: `docker-compose.yml`
3. Test deployment:
   - Trigger manual deploy
   - Verify `https://panchang.karthikwrites.com/health`
   - Check MCP endpoint: `/mcp/sse`

### Phase 4: Ongoing Synchronization

**Sync from Public to Private (Common):**

```bash
cd tamil-panchang
bash scripts/sync_from_public.sh
```

**Sync from Private to Public (Rare):**

```bash
cd tamil-panchang
bash scripts/sync_to_public.sh
```

---

## Automation Scripts

All scripts are located in the `scripts/` directory:

### 1. prepare_public_repo.sh

**Purpose:** Clean up public repository for open-source

**What it does:**
- Backs up production files
- Updates .gitignore
- Removes docker-compose.yml and deploy_instructions.txt from git
- Updates README.md and CLAUDE.md (replaces production URLs)
- Commits and pushes changes

**Usage:**

```bash
cd d:\tamil-panchang-api
bash scripts/prepare_public_repo.sh
```

### 2. create_private_repo.sh

**Purpose:** Create new private repository with production configs

**What it does:**
- Creates private repo on GitHub via `gh` CLI
- Copies entire codebase to new location
- Restores production files from backup
- Initializes git and pushes to private repo
- Sets up `public` remote for syncing

**Usage:**

```bash
cd d:\tamil-panchang-api
bash scripts/create_private_repo.sh
```

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Private repo name: `tamil-panchang`

### 3. sync_from_public.sh

**Purpose:** Sync code changes from public repo to private repo

**What it does:**
- Fetches latest from `public` remote
- Checks for uncommitted changes (stashes if needed)
- Merges `public/main` into `main`
- Pushes to private repo
- Dokploy auto-deploys

**Usage:**

```bash
cd d:\tamil-panchang
bash scripts/sync_from_public.sh
```

**When to use:**
- After merging PRs in public repo
- After adding new features to public repo
- Regular sync to keep private repo updated

### 4. sync_to_public.sh (Optional)

**Purpose:** Sync changes from private repo to public repo (with safety checks)

**What it does:**
- Gets latest commit from private repo
- Checks for production files in commit (warns if found)
- Cherry-picks commit to public repo
- Removes any accidentally included production files
- Pushes to public repo

**Usage:**

```bash
cd d:\tamil-panchang
bash scripts/sync_to_public.sh
```

**When to use:**
- When developing in private repo first
- For production-only bug fixes that should be public

---

## Development Workflow

### Recommended: Develop in Public, Deploy from Private

1. **Create feature branch in public repo:**

   ```bash
   cd tamil-panchang-api
   git checkout -b feature/new-feature
   # Make changes to app.py, etc.
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

2. **Create and merge PR:**

   ```bash
   gh pr create --base main --title "Add new feature"
   gh pr merge
   ```

3. **Sync to private repo:**

   ```bash
   cd ../tamil-panchang
   bash scripts/sync_from_public.sh
   # Dokploy auto-deploys
   ```

4. **Verify deployment:**

   ```bash
   curl https://panchang.karthikwrites.com/health
   ```

### Alternative: Develop in Private, Sync Selectively

1. **Work in private repo:**

   ```bash
   cd tamil-panchang
   git checkout -b feature/new-feature
   # Make changes
   git commit -m "Add new feature"
   git push origin feature/new-feature
   gh pr create && gh pr merge
   ```

2. **If feature should be public:**

   ```bash
   bash scripts/sync_to_public.sh
   ```

---

## Files Modified in Public Repo

### .gitignore

**Add:**

```gitignore
# Private deployment files (never commit)
docker-compose.yml
deploy_instructions.txt
.env
.env.production
.env.local
```

### README.md

**Changes:**
- Replace all `https://panchang.karthikwrites.com` → `http://localhost:8000`
- Add "Live Example" section mentioning the production URL
- Update deployment instructions to focus on `docker-compose.standalone.yml`

**Example:**

```markdown
## Quick Start

### Using Docker (Recommended)

```bash
git clone https://github.com/karthiknitt/tamil-panchang-api.git
cd tamil-panchang-api
docker-compose -f docker-compose.standalone.yml up -d
curl http://localhost:8000/health
```

Access the API at:
- **API Base:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **MCP Server:** http://localhost:8001/sse

### Live Example

This open-source project powers https://panchang.karthikwrites.com -
a free community service for Tamil Panchang calculations.
```

### CLAUDE.md

**Changes:**
- Replace production URLs with `http://localhost:8000`
- Update all `docker-compose` commands to use `docker-compose.standalone.yml`
- Remove references to production Traefik setup

**Example replacements:**

```bash
# OLD:
docker-compose up -d
curl https://panchang.karthikwrites.com/health

# NEW:
docker-compose -f docker-compose.standalone.yml up -d
curl http://localhost:8000/health
```

---

## Files in Private Repo (No Changes)

Keep all files as-is in private repo:
- `docker-compose.yml` - Production with Traefik
- `deploy_instructions.txt` - Private deployment notes
- All source code files
- README.md can keep production URLs

---

## Verification Checklist

### After Phase 1 (Public Repo Cleanup)

- [ ] `docker-compose.yml` removed from git
- [ ] `deploy_instructions.txt` removed from git
- [ ] Backup files created (.backup)
- [ ] `.gitignore` updated
- [ ] No production URLs in README.md examples
- [ ] No production URLs in CLAUDE.md examples
- [ ] Can clone and run: `docker-compose -f docker-compose.standalone.yml up -d`

### After Phase 2 (Private Repo Creation)

- [ ] Private repo created on GitHub
- [ ] All files copied including production configs
- [ ] `docker-compose.yml` restored with Traefik
- [ ] `deploy_instructions.txt` present
- [ ] Remote `public` added for syncing
- [ ] Can verify: `git remote -v` shows both origin and public

### After Phase 3 (Dokploy Configuration)

- [ ] Dokploy pointing to `tamil-panchang` repo
- [ ] Deploy key or token configured
- [ ] Test deployment successful
- [ ] API accessible: `https://panchang.karthikwrites.com`
- [ ] Health check passes: `https://panchang.karthikwrites.com/health`
- [ ] MCP endpoint works: `https://panchang.karthikwrites.com/mcp/sse`

---

## Benefits

1. **Complete separation:** Public and private concerns fully isolated
2. **No exposure risk:** Production configs never in public repo
3. **Clean open-source:** Anyone can clone and run immediately
4. **Simple workflow:** Clear distinction between repos
5. **Automated syncing:** Scripts handle the complexity
6. **Dokploy integration:** Direct deployment from private repo
7. **No env var complexity:** No placeholders or variable substitution

---

## Troubleshooting

### Script Fails: "gh: command not found"

**Solution:** Install GitHub CLI

```bash
# Windows (via winget)
winget install GitHub.cli

# Or download from https://cli.github.com/
```

### Script Fails: "Permission denied"

**Solution:** Make scripts executable

```bash
chmod +x scripts/*.sh
```

### Sync Conflicts

**If merge conflicts occur during sync:**

```bash
# Abort merge
git merge --abort

# Manually resolve
git fetch public
git merge public/main
# Fix conflicts in your editor
git add .
git commit
git push origin main
```

### Dokploy Not Deploying

**Check:**

1. Dokploy has access to private repo (Settings → Repository → Access)
2. Correct branch configured (`main`)
3. Compose file path correct (`docker-compose.yml`)
4. Check Dokploy logs for errors

---

## Quick Reference Commands

### Initial Setup

```bash
# 1. Prepare public repo
cd d:\tamil-panchang-api
bash scripts/prepare_public_repo.sh

# 2. Create private repo
bash scripts/create_private_repo.sh

# 3. Configure Dokploy (manual, via UI)
```

### Regular Development

```bash
# Work in public repo
cd tamil-panchang-api
git checkout -b feature/xyz
# ... make changes ...
git commit && git push
gh pr create && gh pr merge

# Sync to private (auto-deploys)
cd ../tamil-panchang
bash scripts/sync_from_public.sh
```

### Repository Locations

- **Public:** `d:\tamil-panchang-api`
- **Private:** `d:\tamil-panchang`
- **GitHub Public:** `https://github.com/karthiknitt/tamil-panchang-api`
- **GitHub Private:** `https://github.com/karthiknitt/tamil-panchang`

---

## Next Steps

1. **Review this plan**
2. **Run Phase 1:** `bash scripts/prepare_public_repo.sh`
3. **Run Phase 2:** `bash scripts/create_private_repo.sh`
4. **Configure Dokploy** (Phase 3)
5. **Test sync workflow** (Phase 4)
6. **Verify deployment**

---

## Notes

- Scripts are **Windows-compatible** (works in Git Bash)
- All operations are **reversible** (backups created)
- Scripts include **safety checks** (confirm before destructive operations)
- **Dokploy auto-deploys** on push to private repo
- Public repo remains **fully functional** for open-source users

---

*Generated: 2025-12-03*
*Author: Karthik*
*Purpose: Separate open-source repository from private VPS deployment*
