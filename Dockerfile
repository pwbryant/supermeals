# Macrobatics
# Version 1.0

FROM python:3.6

# Install Python and Package Libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client \
    vim

WORKDIR /svr/www/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

# Server
EXPOSE 8000
