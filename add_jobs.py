#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as osp
import hashlib
import time
import glob
import argparse
from hyper_params import ParamGenerator

class HyperParams():
    def __init__(self):
        self.script_name = 'demo.py'
        self.sleep_time = 5
        self.n_depth = 3
        self.n_channel = 32
        self.gpu_memory = 0.1

ROOT_JOB = 'jobs'
TODO_DIR = '{}/todo'.format(ROOT_JOB)
QUEUE_DIR = '{}/queue'.format(ROOT_JOB)
DONE_DIR = '{}/done'.format(ROOT_JOB)
FAIL_DIR = '{}/fail'.format(ROOT_JOB)

def check_job_dirs():
    if not osp.exists(TODO_DIR):
        os.makedirs(TODO_DIR)
    if not osp.exists(QUEUE_DIR):
        os.makedirs(QUEUE_DIR)
    if not osp.exists(DONE_DIR):
        os.makedirs(DONE_DIR)
    if not osp.exists(FAIL_DIR):
        os.makedirs(FAIL_DIR)

def get_command(params):

    cmd = params.script_name
    cmd += ' --sleep_time={}'.format(params.sleep_time)
    cmd += ' --n_depth={}'.format(params.n_depth)
    cmd += ' --n_channel={}'.format(params.n_channel)
    cmd += ' --gpu_memory={}'.format(params.gpu_memory)

    return cmd

def write_shell_script(command, memo=None, params=None):
    hash_str = hashlib.sha256(command.encode('utf-8')).hexdigest()[:16]
    job_name = 'job-{}.sh'.format(hash_str)
    job_file = osp.join(TODO_DIR, job_name)

    pre_cmd = 'OMP_NUM_THREADS=4 python'

    with open(job_file, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write('# [TIME] {}\n'.format(time.asctime()))
        if memo is not None and len(memo) > 0:
            f.write('# [MEMO] {}\n'.format(memo))
        if params is not None and len(params) > 0:
            f.write('# [PARAM] {}\n'.format(params))

        f.write("CMD='{} {}'\n".format(pre_cmd, command))
        f.write('echo $CMD\n'.format(pre_cmd, command))
        f.write('eval $CMD\n'.format(pre_cmd, command))
    print('Create {}'.format(job_file))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dry_run', action='store_const',
                            const=True, default=False,
                            help='dry-run (not save any files)')
    config, unparsed = parser.parse_known_args()
    if len(unparsed) > 0:
        print('[Error] unparsed args: {}'.format(unparsed))
        exit(1)

    pg = ParamGenerator()

    memo = 'run demo.py with various hyper parameters'
    pg.add_params('sleep_time', [5,10,20,30])
    pg.add_params_if('gpu_memory', [0.3, 0.5], cond_key='sleep_time', cond_val=30)
    pg.add_params('n_depth', [3,6,9,12])
    pg.add_params('n_channel', [64,64,32,32], in_series=True)

    all_params = pg.generate(HyperParams(), add_param_string=True)

    if not config.dry_run:
        check_job_dirs()

    for n, params in enumerate(all_params):
        print(n, params.param_string)
        cmd = get_command(params)
        if not config.dry_run:
            write_shell_script(cmd, memo=memo, params=params.param_string)
            time.sleep(0.1) # insert sleep to give a timestamp properly

    total_num_jobs = len(glob.glob(osp.join(TODO_DIR, 'job*sh')))
    print('Add {} jobs and {} jobs are waiting for running'.format(len(all_params), total_num_jobs))