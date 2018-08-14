FROM ubuntu:18.04

RUN apt-get update && apt-get install -y --fix-missing \
    gcc wkhtmltopdf xvfb python2.7 python-pip \
    python-dev build-essential libssl-dev libffi-dev \
    apache2 libapache2-mod-wsgi && \
    #git clone https://github.com/caposseleDigicat/business-ecosystem-charging-backend.git && \
    pip install sh
RUN apt-get install -y wget

WORKDIR business-ecosystem-charging-backend

COPY / ./

RUN mkdir ./src/media && \
    mkdir ./src/media/bills && \
    mkdir ./src/media/assets && \
    #mkdir ./src/plugins && \
    mkdir ./src/user_settings

ENV WORKSPACE=`pwd`

# Install dependencies and sonfigure system to use volume settings
RUN ./python-dep-install.sh && \
    echo "from user_settings.settings import *" > ./src/settings.py

# Create volumes
VOLUME /business-ecosystem-charging-backend/src
VOLUME /business-ecosystem-charging-backend/src/media/bills
VOLUME /business-ecosystem-charging-backend/src/media/assets
VOLUME /business-ecosystem-charging-backend/src/plugins
VOLUME /business-ecosystem-charging-backend/src/user_settings
VOLUME /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins

WORKDIR src

RUN rm wsgi.py
COPY /docker/wsgi.py .

WORKDIR /etc/apache2/
COPY /docker/charging.conf ./sites-available

RUN ln -s ../sites-available/charging.conf ./sites-enabled/charging.conf && \
    sed -i "s|Listen 80|Listen 8006|g" ports.conf

WORKDIR /business-ecosystem-charging-backend/src

COPY /docker/entrypoint.sh /

EXPOSE 8006

ENTRYPOINT ["/entrypoint.sh"]

