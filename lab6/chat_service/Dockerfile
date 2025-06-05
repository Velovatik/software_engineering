# using slim cuz the full image is  huge
FROM python:3.9-slim

# setup working  dir
WORKDIR /app

# install deps  first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  # no cache to keep image  small

# copy everything  else
COPY . .

# start the  server
# TODO: add healthchecks
# TODO: maybe use gunicorn in  prod
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]  # works for  now 