FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN python -m pip install --no-cache-dir pillow numpy requests
# CLI worker: jobs are explicitly invoked; no always-on web process.
CMD ["python", "-c", "print('Salty Saffa editor ready; no background job.')"]
