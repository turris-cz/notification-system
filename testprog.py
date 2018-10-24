#!/usr/bin/env python3

"""Simple Create-Read-Delete test program"""

import json
import os
import pprint

from notifylib.api import Api

conffile = os.path.abspath('config.conf')
expected_template = 'simple.simple'
message_data = '{"message": "egg spam spam"}'

api = Api(conffile)

# Create
templates = api.get_templates()
print(templates)

opts = {
    'skel_id': expected_template,
    'data': json.loads(message_data),
}
nid = api.create(**opts)
print(nid)

# Read

n = api.get_rendered_notification(nid, 'simple', 'en')
pprint.pprint(n)

# Delete

api.call_action(nid, 'dismiss')
