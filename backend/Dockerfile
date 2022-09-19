FROM debian:stable-slim

ENV JIRA_API_KEY = "x3#g7!ndswqo5bbz"
ENV CURRENT_YEAR = 2021
ENV JIRA_USER_ID = "ebs_hrs_api@wisc.edu"
ENV HOST_URL = "https://jira.doit.wisc.edu/jira"

RUN apt-get update

RUN apt-get install -y python3-dev python3-pip 

RUN python3 -m pip install --upgrade pip

WORKDIR /app

COPY . ./
RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

CMD ["python3","server.py"]
