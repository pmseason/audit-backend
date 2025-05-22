FROM ghcr.io/astral-sh/uv:python3.14-rc-bookworm

WORKDIR /app

COPY . .

RUN uv sync --locked

CMD ["uv", "run", "python", "-m", "src.app"]
