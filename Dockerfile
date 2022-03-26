FROM python:3.9-slim AS build
#Update first
RUN apt-get update && apt-get upgrade -y && apt-get install git -y
ADD . /build
WORKDIR /build
RUN pip install --upgrade pip
RUN pip install -U git+https://github.com/Rapptz/discord.py
RUN pip install -r ./requirements.txt

#Multistage build with distroless image
FROM gcr.io/distroless/python3-debian11:nonroot
COPY --from=build --chown=nonroot:nonroot /build /discord_bot
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
WORKDIR /discord_bot
ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages

#Don't generate .pyc files, enable tracebacks on segfaults and disable STDOUT / STDERR buffering
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONHASHSEED 0
ENV TESTING 1
ENV TOKEN $TOKEN
ENV APP_ID $APP_ID
ENV YT_API $YT_API
CMD [ "bot.py", "docker" ]
