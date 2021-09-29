FROM ubuntu:focal


RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install --yes -- \
    software-properties-common \
    apt-transport-https \
    curl && \
    curl --location -- 'https://deb.nodesource.com/gpgkey/nodesource.gpg.key' | apt-key add - && \
    add-apt-repository ppa:neovim-ppa/unstable
COPY ./fs/etc /etc
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install --yes -- \
    zip \
    tmux \
    neovim \
    git \
    python3-venv \
    nodejs


RUN curl -fsSL https://deno.land/x/install/install.sh | sh
ENV PATH="/root/.deno:$PATH"


RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH" \
    TERM=xterm-256color


WORKDIR /
COPY ./fs/code/requirements.txt /code/
RUN pip3 install --no-cache-dir --requirement /code/requirements.txt
COPY ./fs /
RUN python3 -m code.prep


VOLUME [ "/dump" ]
ENTRYPOINT [ "python3", "-m", "code.benchmark" ]
