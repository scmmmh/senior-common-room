FROM python:3.9

RUN apt-get update -y && \
    apt-get dist-upgrade -y && \
    apt-get install -y tini

COPY dist/senior_common_room-0.5.0-py3-none-any.whl /tmp

RUN pip install /tmp/senior_common_room-0.5.0-py3-none-any.whl[postgresql]

ENTRYPOINT [ "tini", "--" ]
CMD [ "python", "-m", "senior_common_room", "server" ]
