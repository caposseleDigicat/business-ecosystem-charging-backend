from os import environ

VERIFY_REQUESTS = environ.get('VERIFY_REQUESTS', 'True').lower() == 'true'

SITE = environ.get('SITE', 'http://localhost:8004/')
LOCAL_SITE = environ.get('LOCAL_SITE', 'http://localhost:8006/')

CATALOG = environ.get('CATALOG', 'http://localhost:8080/DSProductCatalog')
INVENTORY = environ.get('INVENTORY', 'http://localhost:8080/DSProductInventory')
ORDERING = environ.get('ORDERING', 'http://localhost:8080/DSProductOrdering')
BILLING = environ.get('BILLING', 'http://localhost:8080/DSBillingManagement')
USAGE = environ.get('USAGE', 'http://localhost:8080/DSUsageManagement')

RSS = environ.get('RSS', 'http://localhost:8080/DSRevenueSharing')

AUTHORIZE_SERVICE = environ.get('AUTHORIZE_SERVICE', 'http://localhost:8004/authorizeService/token')

# Keyrock/Keystone settings
KEYSTONE_PROTOCOL = environ.get('KEYSTONE_PROTOCOL', 'http')
KEYSTONE_HOST = environ.get('KEYSTONE_HOST', 'localhost')
KEYROCK_PORT = environ.get('KEYROCK_PORT', '3000')
KEYSTONE_PORT = environ.get('KEYSTONE_PORT', '3000')
KEYSTONE_USER = environ.get('KEYSTONE_USER', 'admin@test.com')
KEYSTONE_PWD = environ.get('KEYSTONE_PWD', '1234')
ADMIN_DOMAIN = environ.get('ADMIN_DOMAIN', '')

# App settings (e.g., Orion context broker)
APP_CLIENT_ID =  environ.get('APP_CLIENT_ID', '')

# PEP Proxy Wilma endpoint + /v2/entities
APP_URL = environ.get('APP_URL', 'http://localhost:7000/v2/entities/')
