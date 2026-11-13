FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["sh", "scripts/start_server.sh"]
