# notebook-frontend

A Python package distributing Notebook's static assets only, with no Python dependency.

```bash
git clean -fdx
curl --output notebook-7.4.5-py3-none-any.whl https://files.pythonhosted.org/packages/fe/c7/207fd1138bd82435d13b6d8640a240be4d855b8ddb41f6bf31aca5be64df/notebook-7.4.5-py3-none-any.whl
unzip notebook-7.4.5-py3-none-any.whl
mkdir -p share
cp -r notebook-7.4.5.data/data/share/jupyter share/
cp -r notebook/static src/notebook_frontend/
cp -r notebook/templates src/notebook_frontend/
hatch build
hatch publish
```
