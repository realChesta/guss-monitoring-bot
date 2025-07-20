# Dockerfile
FROM python:3.13-slim

# set a working dir
WORKDIR /app

# copy entire project first (including source code) so that gussbot module is available during installation
COPY . /app

# install the package and its dependencies
RUN pip install --no-cache-dir .

# ensure unbuffered logs
ENV PYTHONUNBUFFERED=1

# default command: start your bot
CMD ["gussbot"]
