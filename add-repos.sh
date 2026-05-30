#!/bin/bash
# Run once to add all your repos as submodules
# Edit GITHUB_USERNAME and REPOS before running

set -e

GITHUB_USERNAME="Eshaan0110"   # <-- your GitHub username

REPOS=(
  "Machine-learning-journey"
  "rl-navigation-agent"
  "cv-fundamentals"
  "Deep-Learning-Journey"
  "Skin-Cancer-Detection-Website"
  "meshmerize"
  "AUV-Mira"
  
  # paste all 29 repo names here
)

mkdir -p repos

for repo in "${REPOS[@]}"; do
  echo "Adding $repo..."
  git submodule add "https://github.com/$GITHUB_USERNAME/$repo.git" "repos/$repo"
done

git add .gitmodules repos/
git commit -m "init: add repos"
git push

echo "Done."
