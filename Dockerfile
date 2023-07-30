FROM cgr.dev/chainguard/python:3.11-dev as builder
WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY tcafe_attending_bot tcafe_attending_bot

RUN python -m venv venv \
    && venv/bin/python -m pip install build \
    && venv/bin/python -m build -w . \
    && python -m pip install --user dist/*.whl

FROM cgr.dev/chainguard/python:3.11
VOLUME ["/home/bhyoo/.local/share/tcafe"]
ENV PATH="${PATH}:/home/nonroot/.local/bin"
ENTRYPOINT ["tcafe-attending-bot"]

# Make sure you update Python version in path
COPY --link --from=builder /home/nonroot/.local /home/nonroot/.local
