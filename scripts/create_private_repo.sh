#!/bin/bash
set -e

echo "=========================================="
echo "Creating Private Production Repository"
echo "=========================================="
echo ""

# Get the parent directory
PARENT_DIR="$(dirname "$(dirname "$0")")"
cd "$PARENT_DIR/.."

echo "Step 1: Creating private repo on GitHub..."
gh repo create tamil-panchang --private --description "Private production deployment for Tamil Panchang API" --confirm
echo "✓ Created private repository"

echo ""
echo "Step 2: Copying codebase to new location..."
if [ -d tamil-panchang ]; then
    echo "Warning: tamil-panchang directory already exists!"
    read -p "Delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf tamil-panchang
    else
        echo "Aborting..."
        exit 1
    fi
fi

cp -r tamil-panchang-api tamil-panchang
cd tamil-panchang
echo "✓ Copied files"

echo ""
echo "Step 3: Restoring production files from backup..."
if [ -f docker-compose.yml.backup ]; then
    mv docker-compose.yml.backup docker-compose.yml
    echo "✓ Restored docker-compose.yml"
fi

if [ -f deploy_instructions.txt.backup ]; then
    mv deploy_instructions.txt.backup deploy_instructions.txt
    echo "✓ Restored deploy_instructions.txt"
fi

echo ""
echo "Step 4: Reinitializing git repository..."
rm -rf .git
git init
git add .
git commit -m "Initial commit for private production repository"
echo "✓ Initialized git"

echo ""
echo "Step 5: Connecting to GitHub..."
git remote add origin https://github.com/karthiknitt/tamil-panchang.git
git branch -M main
echo "✓ Added remote"

echo ""
echo "Step 6: Pushing to GitHub..."
git push -u origin main
echo "✓ Pushed to GitHub"

echo ""
echo "Step 7: Setting up sync with public repo..."
git remote add public https://github.com/karthiknitt/tamil-panchang-api.git
git fetch public
echo "✓ Added public remote"

echo ""
echo "Step 8: Verifying remotes..."
git remote -v

echo ""
echo "=========================================="
echo "✓ Private repository creation complete!"
echo "=========================================="
echo ""
echo "Repository structure:"
echo "  Origin (private):  https://github.com/karthiknitt/tamil-panchang.git"
echo "  Public (sync):     https://github.com/karthiknitt/tamil-panchang-api.git"
echo ""
echo "Next steps:"
echo "  1. Configure Dokploy to use new private repo"
echo "  2. Use sync_from_public.sh to sync changes"
