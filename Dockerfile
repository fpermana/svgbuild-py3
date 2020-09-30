FROM alpine:latest
#FROM alpine:3.11

RUN apk update && apk add --no-cache inkscape python3 py3-pip py3-lxml py3-pillow
RUN pip3 install svg.path --upgrade

COPY . /svgbuild-py3

WORKDIR /svgbuild-py3

