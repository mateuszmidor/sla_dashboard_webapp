# Performance testing

## Platform

- ThinkPad E580 (4xIntel with HyperThreading, 16GB RAM)
- Linux mateusz-ThinkPad-E580 5.11.0-38-generic #42-Ubuntu SMP Fri Sep 24 14:03:54 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
- Python 3.9.5
- Docker version 20.10.7, build 20.10.7-0ubuntu1~21.04.2

## Gunicorn config
```python
wsgi_app = "main:run()"
workers = 1
worker_connections = 1000
bind = ":8050"
timeout = 30
# Worker is changed to prevent worker timeouts
# See: https://github.com/benoitc/gunicorn/issues/1801#issuecomment-585886471
worker_class = "gthread"
threads = # either 1, 3, 5, 7 or 9 - see below
```


## Performance tests

**Gunicorn (workers=1, threads=variable), JMeter (200 users)**

threads: time, req/sec (non-dockerized); time, req/sec (dockerized)  

1:   4:25,  75; 11:27, 30  
3:  3:53,  85; 11:20, 30  
5:  3:48,  88; 11:50, 29  
7:  3:29,  96; 11:35, 29  
9:  2:56. 114; 11:07, 30  

## Load tests

**Gunicorn (workers=1, threads=9), JMeter (300 users)**  
non-dockerized  
60:00, 62 req/s, error 0.0%  

dockerized  
60:00, 15 req/sec, 0.5% error  

## Stres tests

**Gunicorn (workers=1, threads=9), JMeter (600 users)**  
non-dockerized  
55 req/sec, 0.23% err  

dockerized  
27 req/sec/ 0.03% err  