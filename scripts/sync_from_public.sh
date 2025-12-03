#!/bin/bash
set -e

echo "=========================================="
echo "Syncing from Public to Private Repository"
echo "=========================================="
echo ""

# Change to repository root
cd "$(dirname "$0")/.."

echo "Step 1: Fetching latest from public repo..."
git fetch public
echo "✓ Fetched public/main"

echo ""
echo "Step 2: Checking current branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Warning: Not on main branch (currently on $CURRENT_BRANCH)"
    read -p "Switch to main? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
    else
        echo "Aborting..."
        exit 1
    fi
fi

echo ""
echo "Step 3: Checking for uncommitted changes..."
if [ -n "$(git status --porcelain)" ]; then
    echo "Warning: You have uncommitted changes!"
    git status --short
    read -p "Stash changes and continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git stash
        STASHED=true
    else
        echo "Aborting..."
        exit 1
    fi
fi

echo ""
echo "Step 4: Merging public/main into main..."
git merge public/main -m "Sync changes from public repository"
echo "✓ Merged successfully"

echo ""
echo "Step 5: Pushing to private repo..."
git push origin main
echo "✓ Pushed to origin/main"

if [ "$STASHED" = true ]; then
    echo ""
    echo "Step 6: Restoring stashed changes..."
    git stash pop
    echo "✓ Restored stashed changes"
fi

echo ""
echo "=========================================="
echo "✓ Sync complete!"
echo "=========================================="
echo ""
echo "Changes from public repo have been merged into private repo."
echo "Dokploy will auto-deploy on next push."
