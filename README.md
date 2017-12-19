# AWS-Console-Launcher
AWS Web console launcher from CLI


## Prerequisites

### Python libraries
* requests
* boto

pip install boto requests

### IAM

* IAM User with Credentials AccessKey/SecretKey
* IAM Role (to impersonate) with policy(s)
* IAM Role Trust policy
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::012345678901:user/myiamuser"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### AWS CLI credentials

`aws configure --profile MyProfile`


