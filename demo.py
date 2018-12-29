#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import tensorflow as tf
import argparse

def main(config):
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES')
    print('demo.py (#depth={}, #channel={})'.format(config.n_depth, config.n_channel))

    if config.gpu_memory > 0:
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=config.gpu_memory)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        print('Allocate GPU#{} memory and sleep {} sec'.format(gpu, config.sleep_time))

    time.sleep(config.sleep_time)
    print('Done ({})'.format(time.asctime()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--sleep_time', type=int, default=10,
                            help='sleep time (sec)')
    parser.add_argument('--n_depth', type=int, default=3,
                            help='number of depths')
    parser.add_argument('--n_channel', type=int, default=32,
                            help='number of channels')
    parser.add_argument('--gpu_memory', type=float, default=0.1,
                            help='GPU memory usage rate')

    config, unparsed = parser.parse_known_args()
    if len(unparsed) > 0:
        print('[Error] unparsed args: {}'.format(unparsed))
        exit(1)

    main(config)