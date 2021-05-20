FROM python:latest
WORKDIR /usr/src/app/server
COPY . /usr/src/app/server
RUN pip install -r requirements.txt
CMD [ "python", "app.py" ]