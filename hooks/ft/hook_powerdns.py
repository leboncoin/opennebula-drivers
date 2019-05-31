#!/usr/bin/env python
#-*- coding: utf-8 -*-
""" OpenNebula POWERDNS hook """

# Standard library imports
from base64 import b64decode
from datetime import datetime
from json import dumps, loads
from random import randint
from sys import argv

# Third party library imports
from requests import Session
from xmltodict import parse

# Variables
ACTION = 'UPDATE_DNS_ENTRY'
ENV = 'prod'
LOG_FILE = open('/var/log/one/powerdns.log', 'a')
POWERDNS = {
    'api_host': 'powerdns.domain.net',
    'api_key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx',
    'api_port': 8081,
}
PROXY = 'http://proxy.domain.net:3128'
REQ_ID = randint(1, 1000)
SESSION = Session()
TEMPLATE = argv[1]
VERBOSE = True
ZONE = 'domain.net'

def log_me(string, force=False):
    """ Format log """
    if VERBOSE or force:
        LOG_FILE.write('%s [%s]: [%s] %s\n' % (
            datetime.now().strftime("%a %b %H:%M:%S %Y"),
            REQ_ID,
            ACTION,
            string))

def get_args():
    """ Decode args """
    xml_args = b64decode(TEMPLATE)
    return parse(xml_args)

def get_arpa_zone(eth0_ip):
    """
    Evaluate network to identify arpa zone
    """
    return '%s.%s.%s.in-addr.arpa.' % (
        eth0_ip.split('.')[2],
        eth0_ip.split('.')[1],
        eth0_ip.split('.')[0])

def get_arpa_entry(eth0_ip):
    """
    Evaluate network to identify arpa entry
    """
    return '%s.%s.%s.%s.in-addr.arpa.' % (
        eth0_ip.split('.')[3],
        eth0_ip.split('.')[2],
        eth0_ip.split('.')[1],
        eth0_ip.split('.')[0])

def powerdns_get_a(ip_addr):
    """ Verify if record is already in PowerDNS """
    log_me('powerdns_get_a : %s' % ip_addr)

    req = SESSION.get(
        'http://%s:%s/api/v1/servers/localhost/search-data?q=%s' %
        (POWERDNS['api_host'], POWERDNS['api_port'], ip_addr),
        proxies={'http': PROXY},
        headers={'X-API-Key': POWERDNS['api_key']})

    if loads(req.text) == []:
        log_me('No entry in DNS : %s' % ip_addr, force=True)

    a_entry = loads(req.text)[0]['name']
    log_me('A entry : %s' % a_entry)
    return a_entry

def powerdns_delete_record(name_record, type_record, zone):
    """ Add record in PowerDNS via API """
    rrsets = {}
    rrsets['changetype'] = 'DELETE'
    rrsets['type'] = type_record
    rrsets['name'] = name_record
    rrsets['ttl'] = 3600
    payload = {}
    payload['rrsets'] = [rrsets]

    log_me('powerdns payload : %s' % payload)

    req = SESSION.patch(
        'http://%s:%s/api/v1/servers/localhost/zones/%s' %
        (POWERDNS['api_host'], POWERDNS['api_port'], zone),
        data=dumps(payload),
        proxies={'http': PROXY},
        headers={'X-API-Key': POWERDNS['api_key']})
    log_me('return : %s' % req.text)

def powerdns_add_record(name_record, content_record, zone):
    """ Add record in PowerDNS via API """
    record = {}
    record['disabled'] = False
    record['name'] = name_record
    record['set-ptr'] = True
    record['content'] = content_record
    record['type'] = 'A'
    record['priority'] = 0
    rrsets = {}
    rrsets['records'] = [record]
    rrsets['changetype'] = 'REPLACE'
    rrsets['type'] = 'A'
    rrsets['name'] = name_record
    rrsets['ttl'] = 3600
    payload = {}
    payload['rrsets'] = [rrsets]

    log_me('powerdns payload : %s\n' % payload)

    SESSION.patch(
        'http://%s:%s/api/v1/servers/localhost/zones/%s' %
        (POWERDNS['api_host'], POWERDNS['api_port'], zone),
        data=dumps(payload),
        proxies={'http': PROXY},
        headers={'X-API-Key': POWERDNS['api_key']})

def main():
    """ Main class """
    args = get_args()
    log_me('get_args : %s' % args)
    hostname = '%s-%s' % (args['VM']['NAME'], args['VM']['ID'])

    eth0_ip = args['VM']['TEMPLATE']['CONTEXT']['ETH0_IP']

    arpa_zone = get_arpa_zone(eth0_ip)
    arpa_entry = get_arpa_entry(eth0_ip)

    dns_current_a_entry = powerdns_get_a(eth0_ip)
    dns_zone = '.'.join(dns_current_a_entry.split('.')[1:])

    log_me("hostname: %s, dns_zone: %s, arpa_zone: %s, arpa_entry: %s, dns_current_a_entry: %s" % (hostname, dns_zone, arpa_zone, arpa_entry, dns_current_a_entry))

    # Delete provisioning A entry
    powerdns_delete_record(dns_current_a_entry, 'A', dns_zone)

    # Delete provisioning PTR entry
    powerdns_delete_record(arpa_entry, 'PTR', arpa_zone)

    # Add A/PTR real entries
    powerdns_add_record('%s.%s' % (hostname, dns_zone), eth0_ip, dns_zone)


main()

log_me('Done.')
LOG_FILE.close()

exit(0)
