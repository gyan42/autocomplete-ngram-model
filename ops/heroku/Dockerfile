# https://vuejs.org/v2/cookbook/dockerize-vuejs-app.html
# https://cli.vuejs.org/guide/deployment.html#docker-nginx
# build stage
FROM node:lts-alpine as build-stage
#FROM node:latest as build-stage
WORKDIR /app
COPY ui/autocomplete/package.json /app/
ENV PATH /app/node_modules/.bin:$PATH
RUN npm install
COPY ui/autocomplete/.env* /app/
COPY ui/autocomplete/src /app/src
ENV NODE_ENV "heroku"
RUN npm run build -- --mode $NODE_ENV

##################################################################################
# production stage
FROM nginx:stable-alpine as production-stage
#FROM nginx as production-stage
RUN mkdir /app

RUN apk update && apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt /
RUN pip install -r requirements.txt

RUN mkdir /api/
RUN mkdir /data/

COPY data/*.json /data/
COPY main.py /api/
COPY model.py /api/
COPY start.sh /api/

EXPOSE 80 
EXPOSE 8088
EXPOSE 8765

COPY --from=build-stage /app/dist /app

# https://www.tutlinks.com/create-and-deploy-fastapi-app-to-heroku/
# COPY Procfile .

COPY ops/heroku/default.conf /etc/nginx/conf.d/default.conf
# COPY ops/heroku/nginx.conf /etc/nginx/nginx.conf

# CMD ["nginx", "-g", "daemon off;"]


CMD sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf && \
    gunicorn  -b 0.0.0.0:5000 main:app --pythonpath 'api' -k uvicorn.workers.UvicornWorker --pythonpath 'api' --daemon && \ 
    nginx -g 'daemon off;' 
    # uvicorn main:app --host 0.0.0.0 --port 8088  --app-dir=api
    