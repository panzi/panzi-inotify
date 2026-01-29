#!/usr/bin/bash

set -eo pipefail

branch=$(git rev-parse --abbrev-ref HEAD)

if [[ "$branch" = gh-pages ]]; then
    echo 'Already on gh-pages branch!'>&2
    exit 1
fi

. .venv/bin/activate

# This is ugly. I want it to document `panzi_inotify`, which re-expors
# everything from `panzi_inotify.inotify`, but if I point pdoc to
# `panzi_inotify` it doesn't see the doc strings of globals.
pdoc panzi_inotify/inotify -o ./docs

mv docs/panzi_inotify/inotify.html docs/panzi_inotify.html

sed -i 's/panzi_inotify\.inotify/panzi_inotify/' docs/panzi_inotify.html
sed -i 's/panzi_inotify<wbr>\.inotify/panzi_inotify/' docs/panzi_inotify.html
sed -i 's/panzi_inotify\/inotify\.html/panzi_inotify.html/' docs/index.html

rm -r docs/panzi_inotify

git checkout gh-pages

mv docs/*.html docs/*.js .

if git status --porcelain --untracked-files=no | grep '^.M' >/dev/null; then
    git commit *.html *.js -m "updated API documentation"
    git push
    echo "Updated API documentation."
else
    echo 'No changes!'>&2
fi

git checkout "$branch"
