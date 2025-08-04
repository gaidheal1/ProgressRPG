#!/bin/bash

set -e

# Check for dry-run flag
dry_run=false
if [[ "$1" == "--dry-run" ]]; then
  dry_run=true
  echo "🔍 Running in dry-run mode. No changes will be made."
fi

# Get the latest tag, or default to 0.1.0 if none
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.1.0")
echo "Current version: $latest_tag"

# Parse version
version=${latest_tag#v}
IFS='.' read -r major minor patch <<< "$version"

# Ask user for bump type
echo "Select version bump:"
select choice in "Patch ($major.$minor.$((patch + 1)))" \
                  "Minor ($major.$((minor + 1)).0)" \
                  "Major ($((major + 1)).0.0)"; do
  case $REPLY in
    1) new_tag="v$major.$minor.$((patch + 1))"; break ;;
    2) new_tag="v$major.$((minor + 1)).0"; break ;;
    3) new_tag="v$((major + 1)).0.0"; break ;;
    *) echo "Invalid choice. Please enter 1, 2 or 3."; continue ;;
  esac
done

# Confirm
echo "➡️ New tag would be: $new_tag"
read -p "Proceed? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
  echo "❌ Tagging cancelled."
  exit 1
fi

# Get commit messages since last tag
log=$(git log "$latest_tag"..HEAD --pretty=format:"- %s")

# Generate changelog entry
changelog_entry="## $new_tag - $(date +%Y-%m-%d)

$log

"

echo "📝 Generated changelog entry:"
echo "$changelog_entry"

if [[ "$dry_run" = true ]]; then
  echo "✅ Dry run complete. Tag and changelog not written."
  exit 0
fi

# Create Git tag
git tag "$new_tag"
git push origin "$new_tag"

# Prepend changelog entry to CHANGELOG.md (or create file)
if [ -f CHANGELOG.md ]; then
  echo -e "# Changelog\n\n$changelog_entry$(tail -n +2 CHANGELOG.md)" > CHANGELOG.tmp && mv CHANGELOG.tmp CHANGELOG.md
else
  echo -e "# Changelog\n\n$changelog_entry" > CHANGELOG.md
fi

git add CHANGELOG.md
git commit -m "Update changelog for $new_tag"
git push

echo "✅ Tag $new_tag created and CHANGELOG.md updated."
