#!/usr/bin/bash

set -eo pipefail

branch=$(git rev-parse --abbrev-ref HEAD)

if [[ "$branch" = gh-pages ]]; then
    echo 'Already on gh-pages branch!'>&2
    exit 1
fi

pdoc panzi_inotify -o ./docs

git checkout gh-pages

mv docs/*.hml docs/*.js .

if git status --porcelain --untracked-files=no | grep '^.M' >/dev/null; then
    git commit *.html *.js -m "updated API documentation"
    git push
    echo "Updated API documentation."
else
    echo 'No changes!'>&2
fi

git checkout "$branch"
