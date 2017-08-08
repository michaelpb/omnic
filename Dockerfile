# Heavy-weight docker file for development on OmniC
FROM python:3.6.2-stretch
MAINTAINER michaelb <michaelpb@gmail.com>

ENV PYTHONUNBUFFERED 1

RUN groupadd -r omnic \
    && useradd -r -g omnic omnic

# Setup python reqs
COPY ./test/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt \
    && rm /requirements.txt

# Pull in system reqs
# TODO: add in specific versions
RUN apt-get update && apt-get install -y \
    imagemagick \
    inkscape \
    meshlab \
    nodejs \
    openbabel \
    unoconv

# Terrible way to install more recent version of node and npm
RUN curl -sL http://deb.nodesource.com/setup_6.x | bash -
RUN apt-get install nodejs
RUN npm install -g \
    browserify@14.4.0 \
    jsc3d@0.1.8 \
    babel-cli@6.24.1

# Setup code directory
ADD . /app
RUN chown -R omnic /app
USER omnic
WORKDIR /app

EXPOSE 8080

CMD ./bin/omnic runserver
