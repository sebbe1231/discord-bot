FROM python:3.10-alpine

WORKDIR /app

COPY . .

RUN pip install pipenv && \
    pipenv install --deploy --system && \
    pip uninstall pipenv -y

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

CMD /wait && python main.py