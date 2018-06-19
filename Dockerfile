FROM python:2.7

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

RUN pip install -r requirements.txt
RUN pip install gunicorn==19.8.1
RUN pip install MySQL-python==1.2.5

EXPOSE 8080
ENV PLANTAGENET_PORT=8080 \
    PLANTAGENET_HOST=0.0.0.0

CMD ["/opt/plantagenet/docker_start.sh"]
