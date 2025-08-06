## STAGE 1
FROM debian:12 as build

# https://hynek.me/articles/docker-uv/

SHELL ["sh", "-exc"]

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    ca-certificates \
    python3-setuptools \
    python3.11-dev
EOT

COPY --from=ghcr.io/astral-sh/uv:0.4.28 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11 \
    UV_PROJECT_ENVIRONMENT=/app
ENV PATH=/app/bin:$PATH

COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

RUN --mount=type=cache,target=/root/.cache <<EOT
cd /_lock
uv sync \
    --locked \
    --no-dev \
    --no-install-project
EOT

COPY . /src
RUN --mount=type=cache,target=/root/.cache \
    uv pip install \
        --python=$UV_PROJECT_ENVIRONMENT \
        --no-deps \
        /src

## STAGE 2
FROM debian:12

ENV PATH=/app/bin:$PATH

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    python3.11 \
    libpython3.11 \
    libpcre3 \
    libxml2
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

STOPSIGNAL SIGINT

COPY --from=caddy:2.8.4 /usr/bin/caddy /usr/local/bin/caddy

COPY --from=build --chown=app:app /app /app
WORKDIR /app

CMD ["ingress", "control-loop"]
