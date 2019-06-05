FROM python:2.7-alpine

RUN apk add --no-cache \
  bash wget \
  gcc python-dev libffi-dev musl-dev libressl-dev \
  wkhtmltopdf xvfb

WORKDIR business-ecosystem-charging-backend

COPY plugins plugins

# Installing dependencies
ENV WORKSPACE=`pwd`
COPY python-dep-install.sh .
RUN ./python-dep-install.sh

COPY src src

RUN mkdir -p ./src/media/bills && \
    mkdir -p ./src/media/assets

RUN chmod -R 777 ./src/media

# Create volumes
VOLUME /business-ecosystem-charging-backend/src
VOLUME /business-ecosystem-charging-backend/src/media/bills
VOLUME /business-ecosystem-charging-backend/src/media/assets
VOLUME /business-ecosystem-charging-backend/src/plugins
VOLUME /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins

WORKDIR /business-ecosystem-charging-backend/src

COPY /docker/entrypoint.sh /

EXPOSE 8006

ENTRYPOINT ["/entrypoint.sh"]
