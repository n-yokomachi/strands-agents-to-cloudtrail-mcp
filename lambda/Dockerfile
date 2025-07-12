FROM ghcr.io/astral-sh/uv:python3.13-bookworm

# Copy AWS Lambda Web Adapter
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR /app
COPY pyproject.toml README.md /app/
RUN uv sync

COPY . ./

ENV UV_CACHE_DIR=/tmp/uv-cache
ENV UV_NO_SYNC=1 

ENV AWS_LAMBDA_ADAPTER_BUFFER_OFF=1
ENV AWS_LAMBDA_ADAPTER_CALLBACK_PATH="/callback"
ENV AWS_LAMBDA_ADAPTER_HTTP_PROXY_BUFFERING="off"

ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "mcpserver.main:app", "--host", "0.0.0.0", "--port", "8080"] 