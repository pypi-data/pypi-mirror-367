rm -rf dist
uv build
uv publish
git add .
git commit -m "$1"
git push
