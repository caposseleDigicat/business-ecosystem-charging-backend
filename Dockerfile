FROM ubuntu:16.04

RUN apt-get update && apt-get install -y --fix-missing \
    gcc wkhtmltopdf xvfb python2.7 python-pip \
    python-dev build-essential libssl-dev libffi-dev \
    apache2 libapache2-mod-wsgi wget

RUN pip install sh

#ENV VERSION Synchronicity
#ENV VERSION multiple_broker

WORKDIR business-ecosystem-charging-backend

COPY / ./

RUN mkdir -p ./src/media/bills && \
    mkdir -p ./src/media/assets && \
    mkdir -p ./src/user_settings

RUN chmod -R 777 ./src/media

ENV WORKSPACE=`pwd`
RUN ./python-dep-install.sh
RUN echo "from user_settings.settings import *" > ./src/settings.py

# Create volumes
VOLUME /business-ecosystem-charging-backend/src
VOLUME /business-ecosystem-charging-backend/src/media/bills
VOLUME /business-ecosystem-charging-backend/src/media/assets
VOLUME /business-ecosystem-charging-backend/src/plugins
VOLUME /business-ecosystem-charging-backend/src/user_settings
VOLUME /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins

WORKDIR src

WORKDIR /etc/apache2/
COPY /docker/charging.conf ./sites-available

RUN ln -s ../sites-available/charging.conf ./sites-enabled/charging.conf && \
    sed -i "s|Listen 80|Listen 8006|g" ports.conf

WORKDIR /business-ecosystem-charging-backend/src

COPY /docker/entrypoint.sh /

EXPOSE 8006

ENTRYPOINT ["/entrypoint.sh"]
