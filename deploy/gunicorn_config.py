import multiprocessing

bind = "127.0.0.1:5050"
workers = multiprocessing.cpu_count() * 2 + 1
proc_name = 'uniboard'
max_requests = 1000
