#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging, requests, sys, time, json
from retrying import retry, RetryError
from requests.exceptions import HTTPError
from boto3.session import Session

logging.basicConfig(level=logging.INFO)

session = Session(aws_access_key_id='',
                  aws_secret_access_key='',
                  region_name='')
route53Client = session.client('route53')

class HttpGetRunner(object):
    @retry(stop_max_delay=10000)
    def get(self, url):
        logging.info(time.time())
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            raise response.raise_for_status()
        return response

def GetPip():
    url = "https://ifconfig.me/ip"
    runner = HttpGetRunner()
    try:
        response = runner.get(url)
        logging.info(response.headers)
        return response.text
    except HTTPError as e:
        logging.error(e)
    except RetryError as e:
        logging.error(e)
    except Exception as e:
        logging.critical(e)

def SetRecord(SUBDOMAIN, HOST, TTL, pip):
    route53Client.change_resource_record_sets
    hosted_zones = route53Client.list_hosted_zones()['HostedZones']
    for hosted_zone in hosted_zones:
        if hosted_zone["Name"] == HOST :
            hosted_zone_id = hosted_zone["Id"]
    change_batch = {
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': SUBDOMAIN + '.' + HOST ,
                    'Type': 'A',
                    'TTL': TTL,
                    'ResourceRecords': [
                        {'Value': pip}
                    ]
                }
            }
        ]
    }
    try:
        result = route53Client.change_resource_record_sets(
            HostedZoneId = hosted_zone_id,
            ChangeBatch = change_batch
            )
        logging.info(result)
    except Exception as e:
        logging.critical(e)

if __name__ == "__main__":
    HOST = "example.com."
    SUBDOMAIN = "subdomain"
    TTL = 300
    pip = GetPip()
    SetRecord(SUBDOMAIN, HOST, TTL, pip)