#!/usr/bin/sh
# Changes the dir group
# chown -R nobody:nogroup ./web

# worker
celery -A remind_me_django worker -E --without-heartbeat --without-gossip --without-mingle -l info -B
# beat
# celery -A remind_me_django beat --max-interval 1800