FROM ubuntu:focal


RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install --yes -- \
    software-properties-common \
    add-apt-repository ppa:neovim-ppa/unstable && \
    DEBIAN_FRONTEND=noninteractive apt install --yes -- \
    git \
    python3-venv \
    nodejs \
    npm


ENV TERM=xterm-256color
