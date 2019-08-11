"""
Authored by Kim Clarence Penaflor
08/09//2019
version 0.0.2
Documented via reST

Project uxy cli command manager module
"""

import json
import logging
from uxy_cli._generators.aws_setup import AWSSetup
from uxy_cli._generators.proj_setup import ProjSetup

global _appconfig
global _awssetup
global _projsetup
global _projectBlueprint

_appconfig = json.loads(open('uxy_cli/project_template/uxy.json').read())
_projectBlueprint = {}

def _project_setup():
  """
  Initial Project Setup
  """

  global _appconfig
  print('Loading project...')
  projsetup = ProjSetup(_appconfig)
  projsetup._clone()
  projsetup._add_app_config()


def _save_project_blueprint(key, value):
  global _projectBlueprint
  """
  Saves project blueprint for backup
  :param key: json key
  :type key: string
  :param value: json value
  :type value: string
  """

  _projectBlueprint[key] = value


def _aws_setup():
  """
  AWS Resource setup
  """

  global _appconfig
  global _projectBlueprint

  print('Creating AWS Resources...')
  awssetup = AWSSetup(_appconfig)
  awssetup.setup_dynamodb_table()
  _save_project_blueprint('dynamodb:name', _appconfig['app:name']+'-uxy-session-'+_appconfig['app:stage'])

  iamRoleARN = awssetup.setup_iamrole()
  _save_project_blueprint('iam:arn', iamRoleARN)

  lambdaARN = awssetup.package_lambda(iamRoleARN)
  _save_project_blueprint('lambda:arn', lambdaARN)
  _save_project_blueprint('lambda:name', _appconfig['app:name']+'-uxy-app-'+_appconfig['app:stage'])

  restApi = awssetup.setup_uxy_api(lambdaARN)
  _save_project_blueprint('restApi:id', restApi['restApiId'])

  awssetup.save_cloud_config(_projectBlueprint)

  return restApi


def _setup_(appname, runtime, description, stage, region):
  """
  Setup AWS Resources needed
  :param appname: application name
  :type appname: string
  :param runtime: application runtime
  :type runtime: string
  :param description: application short description
  :type description: string
  :param stage: app stage, this also serves as the deployment env.
  :type stage: string
  :param region: aws region
  :type regtion: string
  """

  global _appconfig

  print('\nCreating project: '+appname+'...')

  _appconfig['app:name'] = appname
  _appconfig['app:version'] = '1'
  _appconfig['app:description'] = description
  _appconfig['app:runtime'] = runtime
  _appconfig['app:stage'] = stage
  _appconfig['aws:config']['region'] = region

  _save_project_blueprint('app:name', appname)
  _save_project_blueprint('app:region', region)

  _project_setup()
  apigateway = _aws_setup()



  print('==> Project successfully created!')
  print('API Invocation URL: '+apigateway['invokeURL'])
  print('Use this url to integrate with a facebook app.')
  print('Deploy project with: uxy deploy --[stage]')




