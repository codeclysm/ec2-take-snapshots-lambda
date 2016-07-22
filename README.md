# ec2-take-snapshots-lambda
An AWS Lambda function that takes EC2 snapshots

## Usage
This python script is a meant to be run as a scheduled AWS Lamdba function. This will take a snapshot of all the volumes you specify or every volume that matches a set of tags. You can use this script in conjuction with https://github.com/xombiemp/ec2-purge-snapshots-lambda to create a rolling backup retention plan. You will need to send an event containing these values.
You must populate either the "volumes" key or the "volume_tags" key, but not both.

- "volumes" - List of volume-ids, or "all" for all volumes
    eg. ["vol-12345678", "vol-87654321"] or ["all"]

- "volume_tags" - Dictionary of tags to use to filter the volumes. May specify multiple
    eg. {'key': 'value'} or {'key1': 'value1', 'key2': 'value2', ...}

- "extra_tags" - Dictionary of tags to apply to the created snapshots, in addition to the tags of the instance attached to the volume
    eg. {'key': 'value'} or {'key1': 'value1', 'key2': 'value2', ...}

- "region" - AWS region in which the volumes exist. If empty it defaults to "us-east-1"
    eg. "us-east-1"

- "dry_run" - If it's true, the operations are simulated. The default is true, so you have to explicitly set it to false.
## Configure Lambda function
### IAM Role Policy
Go to the IAM service in the AWS Management console. Click on Roles and click the Create New Role button. Name the role ec2-take-snapshots and click Next Step. Click the Select button that is next to the AWS Lambda service. On the Attach Policy page, don't check any boxes and just click Next Step. Click Create Role. Click on the newly created role and expand the Inline Policies and click where it says click here to create a new policy. Click Custom Policy and click Select. Name the policy ec2-take-snapshots. Copy the contents of the iam_role_policy.json file and paste it in the Policy Document box and click Apply Policy.

### Create Lambda function
#### Configure function
Go to the Lambda service in the AWS Management console. Create a new function and on the Select blueprint page click the Skip button. On the Configure function page fill in the following details:
* Name: ec2-take-snapshots
* Description: An AWS Lambda function that takes EC2 snapshots
* Runtime: Python
* Code box: paste the contents of the ec2_take_snapshots.py file
* Handler: ec2-take-snapshots.main
* Role: ec2-take-snapshots
* Memory: 128
* Timeout: 10 sec
Click the Next button and click Create function.
In the Code tab, configure the variables at the top of the script to your desired configuration. Click Save.

#### Event sources
Click the Event sources tab and click the Add event source link. Choose the type Scheduled Event and fill in the following details:
* Name: ec2-take-snapshots
* Description: Run script hourly
* Schedule Expression: cron(40 * * * ? * )
* Configure input by using a Constant (JSON text) like `{"extra_tags": {"backup":"daily"}, "volumes": ["all"], "dry_run": false}`
Click submit and your function will run every hour at 40 minutes. You can change the cron expression to your desired schedule.

#### Test function
##### Lambda
You can test the function from the Lambda console. Click the Actions button and select Configure test event. Choose Scheduled Event from the drop down. Change the account parameter to your actual AWS account number. Add the following parameter to the structure "noop": "True".  This will tell the script to not actually create any snapshots, but to print that it would have. Now you can press the Save and Test button and you will see the results of the script running in the Lambda console.

##### Locally
You can also test the function locally with the magic of virtualenvs

```bash
$ virtualenv -p /usr/bin/python2.7 venv
$ pip install -r requirements.txt
$ source venv/bin/activate
```

Configure the test event in the `test.py` file according to your preferences

```bash
$ python test.py
```

#### CloudWatch logs
You will be able to see the output when the script runs in the CloudWatch logs. Go to the CloudWatch service in the AWS Management console. Click on Logs and you will see the ec2-take-snapshots log group. Click in it and you will see a Log Stream for every time the script is executed which contains all the output of the script. Go back to the Log Group and click the Never Expire link in the Expire Events After column of the log group row. Change the Retention period to what you feel comfortable with.
