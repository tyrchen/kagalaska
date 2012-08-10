# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__author__ = 'ubuntu'

import os
import sys
import logging

logger = logging.getLogger(__name__)

VENV_PATH = '.virtualenvs'

def get_home():
  return os.getenv('HOME')

def get_venv_path():
  return os.path.join(get_home(), VENV_PATH)

def get_project_path():
  return os.getcwd()

def get_project_name(project_path):
  return filter(None, project_path.split('/'))[-1]

def get_venv_name(project_name, env='dev'):
  return '%s_%s' % (project_name, env)

def build_env(venv_path, venv_name):
  os.chdir(venv_path)
  stdout = os.popen('virtualenv %s --no-site-packages' % venv_name)
  stdout.read()
  
def add_to_env_list(venv_path, venv_name, project_path, filename='.envs.list'):
  f = open(os.path.join(venv_path, filename), mode='a')
  venv = os.path.join(venv_path, venv_name)
  f.write('%s %s %s\n' % (venv_name, project_path, venv))
  f.close()
  print '%s added to env list.' % venv_name


if __name__ == '__main__':
  if len(sys.argv) == 2:
    env = sys.argv[1]
  else:
    env = 'dev'

  project_path = get_project_path()
  project_name = get_project_name(project_path)
  venv_name = get_venv_name(project_name, env)
  venv_path = get_venv_path()
  venv = os.path.join(venv_path, venv_name)

  if os.path.exists(venv):
    print 'Your virtual env is already exists. You can workon it now.'
    exit(-1)

  print 'Project name: %s' % project_name
  print 'Virtual env name: %s' % venv_name
  print 'Build virtualenv now.'

  build_env(venv_path, venv_name)
  print 'Writing to env list now.'

  add_to_env_list(venv_path, venv_name, project_path)
  os.system('workon %s' % venv_name)
  print 'Setting up virtual env done. You can now pip install -r <YOUR REQUIREMENT FILE>'

