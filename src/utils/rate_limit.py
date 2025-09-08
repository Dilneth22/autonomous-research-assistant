import time
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
def retryable(fn, *args, **kwargs):
    return fn(*args, **kwargs)

def backoff_sleep(seconds: float):
    time.sleep(seconds)
