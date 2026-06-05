#!/bin/bash
# Run once to add all your repos as submodules
# Edit GITHUB_USERNAME and REPOS before running

set -e

GITHUB_USERNAME="Eshaan0110"   # <-- your GitHub username

REPOS=(
  # Add your repo names here, one per line:
  # "my-first-repo"
  # "my-second-repo"
  # "my-cool-project"
)

if [ "$GITHUB_USERNAME" = "YOUR_USERNAME" ]; then
  echo "Error: edit GITHUB_USERNAME in this script first"
  exit 1
fi
 
if [ ${#REPOS[@]} -eq 0 ]; then
  echo "Error: add repo names to the REPOS array first"
  exit 1
fi
 
mkdir -p repos
 
for repo in "${REPOS[@]}"; do
  echo "Adding $repo..."
  git submodule add "https://github.com/$GITHUB_USERNAME/$repo.git" "repos/$repo"
done
 
git add .gitmodules repos/
git commit -m "init: add repos"
git push
 
echo "Done — ${#REPOS[@]} repos added."