import time

def sleep_until_next(interval, base_time):
  next_time = max(0, interval - (time.time() - base_time))
  if next_time > 0:
    time.sleep(next_time)
  return time.time()
