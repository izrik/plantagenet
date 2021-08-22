FROM python:3.8.11-alpine3.14

ENV PLANTAGENET_VERSION=0.1
LABEL \
    Name="plantagenet" \
    Version="$PLANTAGENET_VERSION" \
    Summary="A Python blogging system." \
    Description="A Python blogging system." \
    maintaner="izrik <izrik@izrik.com>"

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

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev postgresql-dev libpq && \
    pip install -r requirements.txt && \
    pip install gunicorn==19.8.1 && \
    pip install psycopg2==2.8.6 && \
    apk --purge del .build-deps

EXPOSE 8080
ENV PLANTAGENET_PORT=8080 \
    PLANTAGENET_HOST=0.0.0.0

CMD ["/opt/plantagenet/docker_start.sh"]
