# Jenkins LTS image with Python 3 and curl so pipelines can run unit tests
# and call the Webex API.
FROM jenkins/jenkins:lts-jdk17

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 curl git \
 && rm -rf /var/lib/apt/lists/*
USER jenkins
