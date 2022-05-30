FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN mkdir /app

RUN apt -y update && apt -y upgrade

RUN apt -y install locales locales-all && locale-gen en_US.UTF-8 ru_RU.UTF-8
ENV LC_ALL=ru_RU.UTF-8 LANG=ru_RU.UTF-8 LANGUAGE=ru_RU:ru

# add github
RUN mkdir -p /root/.ssh && ssh-keyscan -t rsa github.com > /root/.ssh/known_hosts
# add ssh key for private repos
ADD build/hovel-build /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# https://dev.im-bot.com/docker-select-caching/
# call build command with `--build-arg REFRESH_REQUIREMENTS=$(date +%s)` to
# force the next layers to be rebuilt
ARG REFRESH_REQUIREMENTS=0

ADD requirements.txt /app/src/

# use cache
RUN python3 -m pip install -r /app/src/requirements.txt -U

ADD . /app/src/

# don't use cache
RUN python3 -m pip install -r /app/src/requirements.txt -U

ADD https://storage.yandexcloud.net/cloud-certs/CA.pem /app/src/yandex.crt

WORKDIR /app/src

EXPOSE 80 8000
