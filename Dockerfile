FROM python:3.12-alpine

RUN mkdir -p /opt/plantagenet

WORKDIR /opt/plantagenet

COPY plantagenet.py \
     LICENSE \
     README.md \
     requirements.txt \
     docker_start.sh \
     ./

COPY static static
COPY templates templates
COPY migrations migrations

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev postgresql-dev g++ && \
    apk add libpq git bash && \
    pip install -r requirements.txt \
                gunicorn==23.0.0 \
                psycopg2==2.9.10 && \
    apk --purge del .build-deps

EXPOSE 8080
ENV PLANTAGENET_PORT=8080 \
    PLANTAGENET_HOST=0.0.0.0

ARG VERSION=unknown
ARG REVISION=unknown

RUN echo "__version__ = '$VERSION'" > __version__.py

ENV PLANTAGENET_REVISION=$REVISION

LABEL \
    Name="plantagenet" \
    Version="$VERSION" \
    Summary="A Python blogging system." \
    Description="A Python blogging system." \
    maintaner="izrik <izrik@izrik.com>"

CMD ["/opt/plantagenet/docker_start.sh"]
