# Macrobatics
# Version 1.0

FROM python:3.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /srv/www/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

# RUN ["chmod", "+x", "/srv/www/app/docker-entrypoint.sh"]
# ENTRYPOINT ["/srv/www/app/docker-entrypoint.sh"]
