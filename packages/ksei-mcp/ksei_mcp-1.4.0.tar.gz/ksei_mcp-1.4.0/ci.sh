rm -rf ./dist

uv version --bump minor

uv build

uv publish