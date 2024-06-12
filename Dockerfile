FROM python:3.10-slim

WORKDIR /app

#Ollama
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    && curl -fsSL https://ollama.com/install.sh | sh

COPY requirements.txt .

RUN  pip install --no-cache-dir -r requirements.txt

COPY . .

COPY start_services.sh /app/start_services.sh
RUN chmod +x /app/start_services.sh

# Expose the port for Ollama
EXPOSE 11434

CMD ["/app/start_services.sh"]

