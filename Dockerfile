# BTC Arbitrage Simulator - single-stage, stdlib only, no pip deps.
FROM python:3.12-slim

WORKDIR /app
COPY app/ ./app/

ENV PORT=8080
EXPOSE 8080

# No requirements to install: the engine and server use only the standard library.
CMD ["python", "app/server.py"]
