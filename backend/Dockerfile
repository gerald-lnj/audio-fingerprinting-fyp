
FROM python:3.8.1

# create workdir
RUN mkdir -p /usr/src/backend

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends gcc and-build-dependencies \
#     && rm -rf /var/lib/apt/lists/* \

# setworkdir
WORKDIR /usr/src/backend

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "backend.py"]