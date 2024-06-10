#!/usr/bin/env python3
""" Elastic APM initialization """

import elasticapm

def init_apm(app_name, apm_server_url, environment):
    apm_client = elasticapm.Client({
        'SERVICE_NAME': app_name,
        'SERVER_URL': apm_server_url, 
        'ENVIRONMENT': environment
    })
    return apm_client
