# Dockerfile
FROM python:3.13-slim

# set a working dir
WORKDIR /app

# copy your Python package files and install dependencies
COPY pyproject.toml hatch.toml* README.md /app/
RUN pip install --no-cache-dir hatch
RUN hatch run pip install --no-cache-dir .

# copy the rest of your code
COPY . /app

# ensure unbuffered logs
ENV PYTHONUNBUFFERED=1

# default command: start your bot
CMD ["gussbot"]
