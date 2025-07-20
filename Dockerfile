# Dockerfile
FROM python:3.13-slim

# set a working dir
WORKDIR /app

# copy project metadata first (leverages Docker layer caching)
COPY pyproject.toml uv.lock hatch.toml* /app/

# install uv (fast replacement for pip) and hatch (used for packaging tasks)
RUN pip install --no-cache-dir uv hatch

# install project dependencies using uv
RUN uv sync --system

# copy the rest of your source code
COPY . /app

# install the local package so the `gussbot` CLI is available
RUN uv pip install --no-cache-dir .

# ensure unbuffered logs
ENV PYTHONUNBUFFERED=1

# default command: start your bot
CMD ["gussbot"]
