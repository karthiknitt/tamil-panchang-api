#!/bin/bash
set -e

echo "=========================================="
echo "Preparing Public Repository for Open-Source"
echo "=========================================="
echo ""

# Change to repository root
cd "$(dirname "$0")/.."

echo "Step 1: Backing up production files..."
if [ -f docker-compose.yml ]; then
    cp docker-compose.yml docker-compose.yml.backup
    echo "✓ Backed up docker-compose.yml"
fi

if [ -f deploy_instructions.txt ]; then
    cp deploy_instructions.txt deploy_instructions.txt.backup
    echo "✓ Backed up deploy_instructions.txt"
fi

echo ""
echo "Step 2: Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Private deployment files (never commit)
docker-compose.yml
deploy_instructions.txt
.env
.env.production
.env.local
EOF
echo "✓ Updated .gitignore"

echo ""
echo "Step 3: Removing production files from git..."
git rm docker-compose.yml
git rm deploy_instructions.txt
echo "✓ Removed production files"

echo ""
echo "Step 4: Updating README.md..."
# Replace production URL with localhost
sed -i 's|https://panchang.karthikwrites.com|http://localhost:8000|g' README.md
# Add live example note at the end of Quick Start section
sed -i '/## Quick Start/a\\n### Live Example\n\nThis open-source project powers https://panchang.karthikwrites.com - a free community service for Tamil Panchang calculations.\n' README.md
echo "✓ Updated README.md"

echo ""
echo "Step 5: Updating CLAUDE.md..."
# Replace production URLs with localhost
sed -i 's|https://panchang.karthikwrites.com|http://localhost:8000|g' CLAUDE.md
# Update docker-compose commands to use standalone
sed -i 's|docker-compose up|docker-compose -f docker-compose.standalone.yml up|g' CLAUDE.md
sed -i 's|docker-compose logs|docker-compose -f docker-compose.standalone.yml logs|g' CLAUDE.md
sed -i 's|docker-compose down|docker-compose -f docker-compose.standalone.yml down|g' CLAUDE.md
echo "✓ Updated CLAUDE.md"

echo ""
echo "Step 6: Staging changes..."
git add .gitignore README.md CLAUDE.md

echo ""
echo "Step 7: Committing changes..."
git commit -m "Prepare repository for open-source release

- Remove production docker-compose.yml (Traefik config)
- Remove private deployment instructions
- Update README and CLAUDE.md to focus on standalone deployment
- Add production files to .gitignore"

echo ""
echo "Step 8: Pushing to GitHub..."
git push origin main

echo ""
echo "=========================================="
echo "✓ Public repository preparation complete!"
echo "=========================================="
echo ""
echo "Backup files created:"
echo "  - docker-compose.yml.backup"
echo "  - deploy_instructions.txt.backup"
echo ""
echo "Next step: Run create_private_repo.sh"
