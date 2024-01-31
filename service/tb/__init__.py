import logging

from tb_rest_client.rest_client_ce import *

from tb_rest_client.rest import ApiException


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


# ThingsBoard REST API URL
url = "http://localhost:8080"

# Default Tenant Administrator credentials
username = "tenant@thingsboard.org"
password = "tenant"


def init():
    with RestClientCE(base_url=url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            
            rest_client.save_tenant_profile({
                "name": "Default",
                "description": "Default tenant profile",
                "isolatedTbRuleEngine": False,
                "profileData": {
                    "configuration": {
                    "type": "DEFAULT",
                    "maxDevices": 0,
                    "maxAssets": 0,
                    "maxCustomers": 0,
                    "maxUsers": 0,
                    "maxDashboards": 0,
                    "maxRuleChains": 0,
                    "maxResourcesInBytes": 0,
                    "maxOtaPackagesInBytes": 0,
                    "transportTenantMsgRateLimit": "1000:1,20000:60",
                    "transportTenantTelemetryMsgRateLimit": "1000:1,20000:60",
                    "transportTenantTelemetryDataPointsRateLimit": "1000:1,20000:60",
                    "transportDeviceMsgRateLimit": "20:1,600:60",
                    "transportDeviceTelemetryMsgRateLimit": "20:1,600:60",
                    "transportDeviceTelemetryDataPointsRateLimit": "20:1,600:60",
                    "maxTransportMessages": 10000000,
                    "maxTransportDataPoints": 10000000,
                    "maxREExecutions": 4000000,
                    "maxJSExecutions": 5000000,
                    "maxDPStorageDays": 0,
                    "maxRuleNodeExecutionsPerMessage": 50,
                    "maxEmails": 0,
                    "maxSms": 0,
                    "maxCreatedAlarms": 1000,
                    "defaultStorageTtlDays": 0,
                    "alarmsTtlDays": 0,
                    "rpcTtlDays": 0,
                    "warnThreshold": 0
                    }
                }
            })


        except ApiException as e:
            logging.exception(e)

