#!/usr/bin/python
import urllib, json
import requests # 'pip install requests'
#from boto3 import STSConnection # AWS SDK for Python (Boto) 'pip install boto'
import boto3
import os


# SECTION A - Variables
# ##############################
# Script VARIABLES -- EDIT THESE
# What is the profile in the CLI or ~/.aws/credentials file you want to use
AWSCLIPROFILE = 'default'

# What is the Role ARN you are going to impersonate
AWSIAMROLEARN = 'arn:aws:iam::012345678901:role/GodMode'

# Browser command -- yep double quoted
# Firefox on Windows from a Ubuntu Bash session
#BROWSERCOMMAND = '"/mnt/c/Program Files (x86)/Mozilla Firefox/firefox.exe"'
# Chrome on Ubuntu (not on Windows)
BROWSERCOMMAND = '/opt/google/chrome/chrome'

# Give the session a name... It will appear in CloudTrail logs and the top right of the console 
AWSSESSIONNAME = AWSCLIPROFILE
# ############################

# SECTION B
# .
# The role you will impersonate needs a trust with the IAM User or source you are 
# connecting with. eg. the secret/access key at AWSCLIPROFILE is for an IAM User
# 1. Go to IAM, Roles, locate the role at AWSIAMROLEARN view the Trust policy/relationship.
# 2. My example
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Effect": "Allow",
#       "Principal": {
#         "AWS": "arn:aws:iam::012345678901:user/myiamuser"
#       },
#       "Action": "sts:AssumeRole"
#     }
#   ]
# }
#
#
# Now we should have a chain of access ...
# IAM User, API Access Key, Trust to Role to enable sts:AssumeRole, Role 
# to assume, Policies linked to assumed role to give access to platform
# 

# SECTION C - The code
# Step 1: Authenticate user in your own identity system.

# Step 2: Using the access keys for an IAM user in your AWS account,
# call "AssumeRole" to get temporary access keys for the federated user

# Note: Calls to AWS STS AssumeRole must be signed using the access key ID 
# and secret access key of an IAM user or using existing temporary credentials.
# The credentials can be in EC2 instance metadata, in environment variables, 
# or in a configuration file, and will be discovered automatically by the 
# STSConnection() function. For more information, see the Python SDK docs:
# http://boto.readthedocs.org/en/latest/boto_config_tut.html
session = boto3.Session(profile_name=AWSCLIPROFILE)
client = session.client('sts')

assumed_role_object = client.assume_role(
    RoleArn=AWSIAMROLEARN,
    RoleSessionName=AWSSESSIONNAME,
)

#print assumed_role_object #["AssumedRoleUser"]
rolecreds = assumed_role_object["Credentials"]

# Step 3: Format resulting temporary credentials into JSON
json_string_with_temp_credentials = '{'
json_string_with_temp_credentials += '"sessionId":"' + rolecreds["AccessKeyId"] + '",'
json_string_with_temp_credentials += '"sessionKey":"' + rolecreds["SecretAccessKey"] + '",'
json_string_with_temp_credentials += '"sessionToken":"' + rolecreds["SessionToken"] + '"'
json_string_with_temp_credentials += '}'

# Step 4. Make request to AWS federation endpoint to get sign-in token. Construct the parameter string with
# the sign-in action request, a 12-hour session duration, and the JSON document with temporary credentials 
# as parameters.
request_parameters = "?Action=getSigninToken"
request_parameters += "&SessionDuration=43200"
request_parameters += "&Session=" + urllib.quote_plus(json_string_with_temp_credentials)
request_url = "https://signin.aws.amazon.com/federation" + request_parameters
r = requests.get(request_url)
# Returns a JSON document with a single element named SigninToken.
signin_token = json.loads(r.text)

# Step 5: Create URL where users can use the sign-in token to sign in to 
# the console. This URL must be used within 15 minutes after the
# sign-in token was issued.
request_parameters = "?Action=login" 
request_parameters += "&Issuer=awsweb.py" 
request_parameters += "&Destination=" + urllib.quote_plus("https://console.aws.amazon.com/")
request_parameters += "&SigninToken=" + signin_token["SigninToken"]
request_url = "https://signin.aws.amazon.com/federation" + request_parameters

# Send final URL to stdout
print request_url
os.system('"' + BROWSERCOMMAND + '" "' + request_url + '"')

