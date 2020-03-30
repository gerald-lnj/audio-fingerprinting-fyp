# use node 12.13.0
FROM node:12.13.0-alpine

# update just in case
# RUN apt-get update

# create workdir
RUN mkdir -p /usr/src/frontend

# setworkdir
WORKDIR /usr/src/frontend

# copy package.json from dev dir to virtual dir
# (not sure of the terms on this)
COPY package.json .

RUN npm i

EXPOSE 8080

CMD [ "npm", "run", "serve"]

COPY . .