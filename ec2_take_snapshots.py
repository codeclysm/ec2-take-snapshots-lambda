from __future__ import print_function
from boto3 import resource

def main(event, context):
    event = validate_event(event)

    ec2 = resource("ec2", region_name=event["region"])

    snap_count = 0

    if "volumes" in event:
        if len(event["volumes"]) == event["volumes"].count("all"):
            volumes = ec2.volumes.all()
        else:
            volumes = []
            for volume_id in event["volumes"]:
                volume = ec2.Volume(volume_id)
                volume.describe_status() # Will raise an exception if it's not found
                volumes.append(volume)
    elif "volume_tags" in event:
        volumes = get_tag_volumes(ec2, event["volume_tags"])
        if volumes.count == 0:
            raise Exception("No volumes found with the given tags.")

    for volume in volumes:
        take_snapshot(volume, event["extra_tags"], ec2, event["dry_run"])
        snap_count += 1

def validate_event(event):
    if "volumes" not in event and "volume_tags" not in event:
        raise Exception('event should contain a volumes or volume_tags key')
    if "extra_tags" not in event:
        event["extra_tags"] = {}
    if "region" not in event:
        event["region"] = "us-east-1"
    if "dry_run" not in event:
        event["dry_run"] = True

    return event

def take_snapshot(volume, extra_tags, ec2, dry_run):
    tags = get_instance_tags(volume, ec2)
    tags.update(extra_tags)
    tags_kwargs = process(tags)
    print(tags_kwargs)

    if not dry_run:
        snapshot = volume.create_snapshot(Description='Created with ec2-take-snapshots')
        if tags_kwargs:
            snapshot.create_tags(**tags_kwargs)
        not_really = ""
    else:
        snapshot = None
        not_really = " (not really)"
    print("Snapshot {} created{} for volume {} with tags {}".format(
          snapshot.snapshot_id if snapshot else "snapshot_id",
          not_really, volume.volume_id, tags_kwargs["Tags"])
          )

def get_instance_tags(volume, ec2):
    if len(volume.attachments) < 1:
        return {}
    id = volume.attachments[0]["InstanceId"]
    instance = ec2.Instance(id)

    # Convert the tags into the snapshot format
    tags = {}
    for tag in instance.tags:
        if "aws:" in tag["Key"]:
            continue
        tags[tag["Key"]] = tag["Value"]
    return tags

def get_tag_volumes(ec2, tags):
    collection_filter = []
    for key, value in tags.iteritems():
        collection_filter.append(
            {
                "Name": "tag:" + key,
                "Values": [value]
            }
        )
    tag_volumes = ec2.volumes.filter(Filters=collection_filter)
    iterator = (i for i in tag_volumes)
    count = sum(1 for _ in iterator)
    tag_volumes.count = count
    return tag_volumes

def process(tags):
    processed_tags = []
    tags_kwargs = {}
    # AWS allows 10 tags per resource
    if tags and len(tags) <= 10:
        for key, value in tags.iteritems():
            processed_tags.append({'Key': key, 'Value': value})
        tags_kwargs['Tags'] = processed_tags
    return tags_kwargs
