FROM python:3.12-slim

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org pip poetry setuptools wheel -U --no-cache-dir


ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' 

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN poetry install --no-root && mkdir data

COPY . /code

RUN chmod a+x /code/run.sh && sed -i -e '$a\'$'\n''DB_PATH="/code/data/test.db"' /code/marketplaats-bot/.env
RUN echo | ls /code/marketplaats-bot/ && echo | cat /code/marketplaats-bot/.env && echo | cat /code/marketplaats-bot/runcounter.txt

CMD ["/code/run.sh"]
