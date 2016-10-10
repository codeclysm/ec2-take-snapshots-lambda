import logging

from ec2_take_snapshots import *

logging.basicConfig()

event = {
    "volumes": ["all"],
    # "volumes": ["vol-5efa71fa", "vol-788568d2"],
    # "volume_tags": {"backup": "true"},
    "extra_tags": {"backup": "daily"},
    "dry_run": True
}
context = {}

main(event, context)
