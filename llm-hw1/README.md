# Docker Compose Setup for Elasticsearch and Python App

This repository contains a Docker Compose setup for running an Elasticsearch instance along with a Python application require for the homework1. The Python application can be used to interact with the Elasticsearch service.

## Prerequisites

- Docker
- Docker Compose

## Services

- **elasticsearch**: Runs an Elasticsearch instance.
- **python-app**: Runs a Python application that can interact with Elasticsearch.

## Running the hw script

```sh
git clone <repository_url>
cd llm-hw1
docker-compose up -d --build
docker exec -it python-app /bin/bash
cd app
python fetch.py
