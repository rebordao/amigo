FROM alpine:3.2

RUN apk add --update musl python3 \
    && pip3 install --upgrade pip \
    && rm /var/cache/apk/*

RUN mkdir ~/amigo
ADD . ~/amigo
WORKDIR ~/amigo
RUN pip3 install -r requirements.txt

