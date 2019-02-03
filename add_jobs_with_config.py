#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as osp
import hashlib
import time
import glob
import argparse
import yaml
import copy
from hyper_params import ParamGenerator

ROOT_JOB = 'jobs'
TODO_DIR = '{}/todo'.format(ROOT_JOB)
QUEUE_DIR = '{}/queue'.format(ROOT_JOB)
DONE_DIR = '{}/done'.format(ROOT_JOB)
FAIL_DIR = '{}/fail'.format(ROOT_JOB)
PARAM_DIR = '{}/param'.format(ROOT_JOB)

default_params = {
    'script_name': 'demo_with_config.py',
    'default_config_path': 'config.yaml'
}

def check_job_dirs():
    for subdir in [ROOT_JOB, TODO_DIR, QUEUE_DIR, DONE_DIR, FAIL_DIR, PARAM_DIR]:
        if not osp.exists(subdir):
            os.makedirs(subdir)

def get_command(params):

    cmd = 'OMP_NUM_THREADS=4 python {}'.format(params['script_name'])
    cmd += ' --config_path=${PARAM_DIR}/'+osp.basename(params['config_path']) # $PARAM_DIR is defined when dumping the script 

    return cmd

def write_shell_script(command, job_path, memo=None, params=None):

    with open(job_path, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write('#TIME: {}\n'.format(time.asctime()))
        if memo is not None and len(memo) > 0:
            f.write('#MEMO: {}\n'.format(memo))
        if params is not None and len(params) > 0:
            f.write('#PARAM: {}\n'.format(params))

        f.write('SCRIPT_DIR=$(cd $(dirname $0); pwd)\n')
        f.write('PARAM_DIR="${SCRIPT_DIR}/../param/"\n')
        f.write('CMD="{}"\n'.format(command))
        f.write('echo $CMD\n')
        f.write('eval $CMD\n')
    print('Create {}'.format(job_path))

def copy_config(default_config, params):

    config = copy.deepcopy(default_config)

    for tagpath, value in params.items():
        tags = tagpath.split('/')
        subconfig = config
        for i, tag in enumerate(tags):
            if tag in subconfig:
                if i != len(tags)-1:
                    # not the end
                    assert isinstance(subconfig[tag], dict), 'May typo {}'.format(tagpath)
                    subconfig = subconfig[tag]
                else:
                    subconfig[tag] = value
            else:
                assert i == 0
                pass # ignore param
    return config

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dry_run', action='store_const',
                            const=True, default=False,
                            help='dry-run (not save any files)')
    args, unparsed = parser.parse_known_args()
    if len(unparsed) > 0:
        print('[Error] unparsed args: {}'.format(unparsed))
        exit(1)

    with open(default_params['default_config_path']) as f:
        default_config = yaml.load(f)

    pg = ParamGenerator()

    memo = 'run demo.py with various hyper parameters'
    pg.add_params('sleep_time', [5,10,20,30])
    pg.add_params_if('device/gpu_memory', [0.3, 0.5], cond_key='sleep_time', cond_val=30)
    pg.add_params('model/n_depth', [3,6,9,12])
    pg.add_params('model/n_channel', [64,64,32,32], in_series=True)

    all_params = pg.generate(default_params, add_param_string=True)

    if not args.dry_run:
        check_job_dirs()

    for n, params in enumerate(all_params):
        print(n, params['__PARAM__'])
        config =  copy_config(default_config, params)

        hashstr = hashlib.sha256(params['__PARAM__'].encode('utf-8')).hexdigest()[:16]
        config_path = osp.join(PARAM_DIR, '{}.yaml'.format(hashstr))
        job_path = osp.join(TODO_DIR, '{}.sh'.format(hashstr))
        params['config_path'] = config_path

        cmd = get_command(params)
        if not args.dry_run:
            write_shell_script(cmd, job_path, memo=memo, params=params['__PARAM__'])
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            time.sleep(0.1) # insert sleep to give a timestamp properly

    total_num_jobs = len(glob.glob(osp.join(TODO_DIR, 'job*sh')))
    print('Add {} jobs and {} jobs are waiting for running'.format(len(all_params), total_num_jobs))