# build env
FROM node:13.12.0-alpine as build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . ./

RUN npm run build

CMD cp -r build result_build

RUN apk add --upgrade apk-tools

RUN apk update

RUN apk add mc tree nano
