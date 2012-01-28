# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
VERSION = "0.4"
USER_AGENT = 'python-cloudb/%s' % VERSION

# Default AUTH SERVER
DEFAULT_AUTH_SERVER = "https://auth.api.rackspacecloud.com/v1.1/auth"

# UK AUTH SERVER
UK_AUTH_SERVER = "https://lon.auth.api.rackspacecloud.com/v1.1/auth"

# Default URL for Regions
REGION_URL = "https://%s.loadbalancers.api.rackspacecloud.com/v1.0"

# Different available Regions
REGION = {
    "chicago": "ord",
    "dallas": "dfw",
    "london": "lon",
}

# Allowed Protocol
LB_PROTOCOLS = ["FTP", "HTTP", "IMAPv4", "POP3", "LDAP",
                "LDAPS", "HTTPS", "IMAPS",
                "POP3S", "SMTP", "TCP"]

# Attributed allowed to be modified on loadbalancers
LB_ATTRIBUTES_MODIFIABLE = ["name", "algorithm", "protocol", "port"]

# Types of VirtualIPS
VIRTUALIP_TYPES = ["PUBLIC", "SERVICENET"]

# HealthMonitors Types
HEALTH_MONITOR_TYPES = ['CONNECT', 'HTTP', 'HTTPS']

# SessionPersistence Types
SESSION_PERSISTENCE_TYPES = ['HTTP_COOKIE']
