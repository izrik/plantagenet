#!/bin/sh

python /opt/plantagenet/plantagenet.py --create-db
gunicorn -b $PLANTAGENET_HOST:$PLANTAGENET_PORT plantagenet:app
