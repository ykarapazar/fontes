# Fontes as a stdio MCP server in a container (used by directories such as Glama to build
# and inspect the server). Most people should use the installer or `uvx fontes-mcp` instead.
#   docker build -t fontes .
#   docker run -i --rm fontes            # speaks MCP on stdin/stdout
# API keys, if needed: docker run -i --rm -e WLM_FR_PISTE_CLIENT_ID=… -e WLM_FR_PISTE_CLIENT_SECRET=… fontes
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

# Only what the package build needs (see [tool.hatch.build] in pyproject.toml).
COPY pyproject.toml uv.lock README.md LICENSE NOTICE ./
COPY src ./src
COPY installer/fontes_i18n.py ./installer/fontes_i18n.py
COPY installer/locales ./installer/locales
RUN uv sync --frozen --no-dev --no-editable

# No in-container update notice: the image is rebuilt for each release.
ENV PATH="/app/.venv/bin:$PATH" FONTES_NO_UPDATE_CHECK=1
RUN useradd --create-home fontes
USER fontes

ENTRYPOINT ["fontes"]
