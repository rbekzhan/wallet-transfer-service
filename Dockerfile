FROM python:3.11 as builder

ENV WORKDIR="/source"
ENV VENV_PATH="/source/.venv"
ENV POETRY_HOME="/opt/poetry"

WORKDIR $WORKDIR

RUN apt-get update && apt-get install --no-install-recommends -y curl
RUN python -m venv .venv
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
RUN $VENV_PATH/bin/pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml
RUN poetry install
COPY src/ ./src
RUN poetry build
RUN $VENV_PATH/bin/pip install $WORKDIR/dist/*.tar.gz && $VENV_PATH/bin/pip check

FROM python:3.11 as api

COPY --from=builder /source/.venv /source/.venv
RUN ln -snf /source/.venv/bin/run_api /usr/local/bin/

CMD ["run_api"]
