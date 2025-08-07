from functools import wraps
import time

def stopwatch(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        print(f''''{function.__name__}' was completed in {(end_time - start_time):.2f} seconds.''')

        return result

    return wrapper
