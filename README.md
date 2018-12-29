# job-runner

This is a general purpose job-runner repogitory, which is especially useful for deep learning training and testing (e.g. grid search hyper parameter tuning).

## Run demo
The sample codes is for running demo.py with different arguments.
You need to create jobs in `jobs/todo/` first. The sample script are provided and you can try it by doing 
```
./add_jobs.py 
```

ParamGenerator (in hyper_params.py) enable you to prepare arbitrary combination of hyper parameters. 
For example, the following codes can generate 20 patterns (gpu_memory will be changed only if sleep_time is equal to 30, and n_depth and n_channel will be changed in sync.)

```python
pg.add_params('sleep_time', [5,10,20,30])
pg.add_params_if('gpu_memory', [0.3, 0.5], cond_key='sleep_time', cond_val=30)
pg.add_params('n_depth', [3,6,9,12])
pg.add_params('n_channel', [64,64,32,32], in_series=True)
```

In order to run a job script, you just type
```
./run.py --gpu=0
``` 
Then the oldest job will be executed with GPU#0 and stored `jobs/done` if it finishes successfully.

When you want to run all jobs back-to-back, you just type the following command
```
./run.py --gpu=0 --mode=monitor
```

It is also possible to run multi process with different gpus by doing something like this.
(Do it from independent terminals such as tmux)
```
./run.py --gpu=0 --mode=monitor
./run.py --gpu=1 --mode=monitor
./run.py --gpu=2 --mode=monitor
```

