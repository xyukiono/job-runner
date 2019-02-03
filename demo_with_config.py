#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import tensorflow as tf
import argparse
import yaml

def main(config):
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES')
    print('demo_with_config.py (#depth={}, #channel={})'.format(config['model']['n_depth'], config['model']['n_channel']))

    if config['device']['gpu_memory'] > 0:
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=config['device']['gpu_memory'])
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        print('Allocate GPU#{} memory and sleep {} sec'.format(gpu, config['sleep_time']))

    time.sleep(config['sleep_time'])
    print('Done ({})'.format(time.asctime()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config_path', type=str, default='config.yaml',
                            help='config path (YAML format)')

    args, unparsed = parser.parse_known_args()
    if len(unparsed) > 0:
        print('[Error] unparsed args: {}'.format(unparsed))
        exit(1)

    with open(args.config_path) as f:
        config = yaml.load(f)

    main(config)