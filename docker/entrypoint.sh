#!/usr/bin/env bash

function test_connection {
    echo "Testing $1 connection"
    exec 10<>/dev/tcp/$2/$3
    STATUS=$?
    I=0

    while [[ ${STATUS} -ne 0  && ${I} -lt 50 ]]; do
        echo "Connection refused, retrying in 5 seconds..."
        sleep 5

        if [[ ${STATUS} -ne 0 ]]; then
            exec 10<>/dev/tcp/$2/$3
            STATUS=$?

        fi
        I=${I}+1
    done

    exec 10>&- # close output connection
    exec 10<&- # close input connection

    if [[ ${STATUS} -ne 0 ]]; then
        echo "It has not been possible to connect to $1"
        exit 1
    fi

    echo "$1 connection, OK"
}

# Validate that mandatory parameters has been provided
if [ -z $PAYPAL_CLIENT_ID ]; then
    echo 'PAYPAL_CLIENT_ID environment variable not set'
    exit 1
fi

if [ -z $PAYPAL_CLIENT_SECRET ]; then
    echo 'PAYPAL_CLIENT_SECRET environment variable not set'
    exit 1
fi

if [ -z $CATALOG ]; then
    echo 'CATALOG environment variable not set'
    exit 1
fi

if [ -z $RSS ]; then
    echo 'RSS environment variable not set'
    exit 1
fi

if [ -z $INVENTORY ]; then
    echo 'INVENTORY environment variable not set'
    exit 1
fi

# Ensure mongodb is running

if [ -z ${DB_HOST} ]; then
    DB_HOST=localhost
fi

if [ -z ${DB_PORT} ]; then
    DB_PORT=27017
fi

test_connection "MongoDB" ${DB_HOST} ${DB_PORT}

# Check that the required APIs are running
APIS_HOST=`echo $CATALOG | grep -o "://.*:" | grep -oE "[^:/]+"`
APIS_PORT=`echo $CATALOG | grep -oE ":[0-9]+" | grep -oE "[^:/]+"`

test_connection "APIs" ${APIS_HOST} ${APIS_PORT}

# Check that the RSS is running
RSS_HOST=`echo $RSS | grep -o "://.*:" | grep -oE "[^:/]+"`
RSS_PORT=`echo $RSS | grep -oE ":[0-9]+" | grep -oE "[^:/]+"`
test_connection "RSS" ${RSS_HOST} ${RSS_PORT}

################### TEST APIS CONNECTION FIRST #######################
# Get glassfish host and port from config
INVENTORY_HOST=`echo $INVENTORY | grep -o "://.*:" | grep -oE "[^:/]+"`
INVENTORY_PORT=`echo $INVENTORY | grep -oE ":[0-9]+" | grep -oE "[^:/]+"`
#test_connection 'INVENTORY' ${INVENTORY_HOST} ${INVENTORY_PORT}

#GLASSFISH_HOST=`/business-ecosystem-logic-proxy/node-v6.9.1-linux-x64/bin/node getConfig glasshost`
#GLASSFISH_PORT=`/business-ecosystem-logic-proxy/node-v6.9.1-linux-x64/bin/node getConfig glassport`

#INVENTORY_PATH=`DSProductInventory`

echo "Testing INVENTORY APIs deployed"
wget http://${INVENTORY_HOST}:${INVENTORY_PORT}/DSProductInventory
STATUS=$?
I=0
while [[ ${STATUS} -ne 0  && ${I} -lt 50 ]]; do
    echo "INVENTORY APIs not deployed yet, retrying in 5 seconds..."

    sleep 5
    wget http://${INVENTORY_HOST}:${INVENTORY_PORT}/DSProductInventory
    STATUS=$?

    I=${I}+1
done

echo "Installing Orion Plugin"

touch /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/__init__.py

/business-ecosystem-charging-backend/src/manage.py loadplugin /business-ecosystem-charging-backend/plugins/Orion.zip

if [ ! -d /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/orion-query ]; then
    mkdir /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/orion-query
fi

touch /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/orion-query/__init__.py

cp /business-ecosystem-charging-backend/plugins/orion-query/* /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/orion-query/


echo "Installing HistoricalAPI Plugin"
/business-ecosystem-charging-backend/src/manage.py loadplugin /business-ecosystem-charging-backend/plugins/Historical.zip

if [ ! -d /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/historicalapi-query ]; then
    mkdir /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/historicalapi-query
fi

touch /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/historicalapi-query/__init__.py

cp /business-ecosystem-charging-backend/plugins/historicalapi-query/* /business-ecosystem-charging-backend/src/wstore/asset_manager/resource_plugins/plugins/historicalapi-query/

echo "Starting charging server"
gunicorn -b 0.0.0.0:8006 wsgi:application
