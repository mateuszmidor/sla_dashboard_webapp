# syntax=docker/dockerfile:1
FROM python:3.9-slim

ARG USER=sla-dashboard-user
RUN useradd --create-home ${USER}
USER ${USER}
ENV PATH=/home/${USER}/.local/bin:$PATH

WORKDIR /app
COPY domain domain
COPY infrastructure infrastructure
COPY presentation presentation
COPY generated generated
COPY main.py .
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--config=data/gunicorn.conf.py", "main:run()"]