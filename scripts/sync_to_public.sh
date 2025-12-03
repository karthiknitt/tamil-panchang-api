#!/bin/bash
set -e

echo "=========================================="
echo "Syncing from Private to Public Repository"
echo "=========================================="
echo ""

# Get the public repo path
PUBLIC_REPO="../tamil-panchang-api"

if [ ! -d "$PUBLIC_REPO" ]; then
    echo "Error: Public repository not found at $PUBLIC_REPO"
    exit 1
fi

echo "Step 1: Getting latest commit from private repo..."
COMMIT_HASH=$(git log -1 --format="%H")
COMMIT_MSG=$(git log -1 --format="%s")
echo "Latest commit: $COMMIT_HASH"
echo "Message: $COMMIT_MSG"

echo ""
echo "Step 2: Checking for production files in commit..."
PROD_FILES=$(git diff-tree --no-commit-id --name-only -r $COMMIT_HASH | grep -E "(docker-compose\.yml|deploy_instructions\.txt)" || true)

if [ -n "$PROD_FILES" ]; then
    echo "Warning: Production files detected in commit:"
    echo "$PROD_FILES"
    echo "These should NOT be synced to public repo!"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting..."
        exit 1
    fi
fi

echo ""
echo "Step 3: Switching to public repo..."
cd "$PUBLIC_REPO"

echo ""
echo "Step 4: Cherry-picking commit..."
git fetch ../tamil-panchang main
git cherry-pick $COMMIT_HASH

echo ""
echo "Step 5: Removing any accidentally included production files..."
if [ -f docker-compose.yml ]; then
    git rm docker-compose.yml
    echo "✓ Removed docker-compose.yml"
fi

if [ -f deploy_instructions.txt ]; then
    git rm deploy_instructions.txt
    echo "✓ Removed deploy_instructions.txt"
fi

# Check if there are staged changes to amend
if [ -n "$(git diff --cached --name-only)" ]; then
    git commit --amend --no-edit
    echo "✓ Amended commit to remove production files"
fi

echo ""
echo "Step 6: Pushing to public repo..."
git push origin main

echo ""
echo "=========================================="
echo "✓ Sync complete!"
echo "=========================================="
echo ""
echo "Changes synced to public repository (without production files)."
