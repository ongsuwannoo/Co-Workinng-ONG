ARG PYTHON_VERSION=3.8.6

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV SECRET_KEY "55XzofHho6Rb7g04Zy0wRPp40AXjwv1cki0KlbTh4riMZUyQOC"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "main.wsgi"]
