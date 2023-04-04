FROM python:3.9-slim
WORKDIR /app
COPY app/ /app/
RUN pip install -r requirements.txt

RUN apt-get update -y
RUN apt-get install -y ffmpeg


ENV FLASK_APP=app.py
ENV FLASK_DEBUG=False

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]

