#!/bin/bash
set -e

cd "$(git rev-parse --show-toplevel)" || exit 1

# shellcheck disable=SC1091
source tools/ci/.envrc

set +e
IFS=',' read -r -a BRANCHES <<< "${UPDATE_BRANCHES}"
set -e

echo "Update branches ${BRANCHES[*]}"

git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"

if [[ -f $(git rev-parse --git-dir)/shallow ]]; then
  git fetch --unshallow --quiet
fi

git fetch origin -n "${DEFAULT_BRANCH}:refs/remotes/origin/${DEFAULT_BRANCH}"

for BRANCH in ${BRANCHES[*]}
do
  git fetch origin -n "${BRANCH}:refs/remotes/origin/${BRANCH}"
  git branch -f "${BRANCH}" "origin/${BRANCH}"
  git checkout "${BRANCH}"
  COMMIT_MESSAGE="Merge remote-tracking branch 'origin/${DEFAULT_BRANCH}' into ${BRANCH} update-branches"
  git merge "origin/${DEFAULT_BRANCH}" -m "${COMMIT_MESSAGE}"
  MODIFIED_FILES=$(git diff --name-only HEAD HEAD~1)
  echo "MODIFIED_FILES=${MODIFIED_FILES}"
  if [ -z "${MODIFIED_FILES:-}" ]; then
    COMMIT_MESSAGE_HEAD="$(git log --format=%B -n 1 HEAD)"
    if [ "${COMMIT_MESSAGE}" == "${COMMIT_MESSAGE_HEAD}" ]; then
      COMMIT_MESSAGE="${COMMIT_MESSAGE} [actions skip]"
      git commit --amend -m "${COMMIT_MESSAGE}"
    fi
  fi
  git push origin "${BRANCH}"
done