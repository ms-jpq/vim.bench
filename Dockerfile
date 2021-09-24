FROM ubuntu:focal


RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install --yes -- \
    software-properties-common && \
    add-apt-repository ppa:neovim-ppa/unstable && \
    DEBIAN_FRONTEND=noninteractive apt install --yes -- \
    tmux \
    neovim \
    git \
    python3-venv \
    nodejs \
    npm


RUN python3 -m venv /venv && \
    python3 -m venv /srv/venv

ENV PATH="/venv/bin:$PATH" \
    TERM=xterm-256color


COPY ./fs/code/requirements.txt /code/
RUN pip3 install --requirement /code/requirements.txt
COPY ./fs /


WORKDIR /
ENTRYPOINT [ "python3", "-m", "code" ]
CMD [ "--lo", "0.005", "--hi", "0.01", "--chars", "888" ]
