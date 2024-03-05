FROM  alpine

WORKDIR /app
COPY main.py prepro.py /app/
ENV DEBIAN_FRONTEND=noninteractive

RUN apk update &&\
    apk upgrade &&\
    apk add python3 &&\
    apk add py3-pip &&\
    apk add ffmpeg &&\
    pip3 install fastapi uvicorn python-multipart watchdog moviepy pydub python-mimeparse &&\
    pip3 install os-sys || true

EXPOSE 2100

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","2100", "--reload"]
