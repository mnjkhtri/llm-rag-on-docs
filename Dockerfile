FROM python:3.10-slim

WORKDIR /app

#Ollama
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    && curl -fsSL https://ollama.com/install.sh | sh


COPY . .

RUN  pip install -r requirements.txt

COPY start.sh /start.sh
RUN chmod +x /app/start.sh

# Expose the port for Ollama
EXPOSE 11434

CMD ["/start_services.sh"]

