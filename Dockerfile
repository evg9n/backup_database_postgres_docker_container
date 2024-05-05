FROM python:3.10.12-slim

WORKDIR /app

#RUN python -m pip install --upgrade pip

RUN python -m pip install --upgrade pip && apt-get update && \
    apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
    apt-get update && \
    apt-get install -y docker-ce-cli

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]