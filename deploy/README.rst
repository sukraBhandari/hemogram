========================================
 Deploymemnts for the app and resources
========================================

setup
=====

Install the virtualenv::

  python3 -m venv py3-env
  source py3-env/bin/activate
  pip install -U pip
  pip install ansible boto3

deployment
==========

Deploy the S3 bucket ``hemogram-data`` and accompanying IAM role ``HemogramUser``::

  ./deploy-bucket.yml

Create an access key for the IAM user::

  aws iam create-access-key --user-name HemogramUser



