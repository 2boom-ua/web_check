FROM python:3.11-slim
WORKDIR /web_check

COPY . /web_check

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "web_check.py"]

