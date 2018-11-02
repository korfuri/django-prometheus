#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

os.chdir('django_prometheus/tests/end2end')


exit(subprocess.call(['python', 'manage.py' ,'test']))
