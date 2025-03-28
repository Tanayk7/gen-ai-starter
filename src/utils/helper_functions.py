import os
from datetime import datetime, timezone
import yaml
from textwrap import wrap
from functools import wraps
import time

# for loading configs to environment variables
def load_config(file_path):
    # Define default values
    default_values = {
        'SERPER_API_KEY': 'default_serper_api_key',
        'OPENAI_API_KEY': 'default_openai_api_key',
        'SERPER_API_KEY': 'default_groq_api_key',
    }
    
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            # If the value is empty or None, load the default value
            if not value:
                os.environ[key] = default_values.get(key, '')
            else:
                os.environ[key] = value

# for getting the current date and time in UTC
def get_current_utc_datetime():
    now_utc = datetime.now(timezone.utc)
    current_time_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
    return current_time_utc

def timed_exec(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        start_time = time.time()
        return_value = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time  # Calculate the difference
        print(f"Execution time: {execution_time} seconds")
        return return_value if return_value != None else None
    return inner

def custom_print(message, stdscr=None, scroll_pos=0):
    if stdscr:
        max_y, max_x = stdscr.getmaxyx()
        max_y -= 2  # Leave room for a status line at the bottom

        wrapped_lines = []
        for line in message.split("\n"):
            wrapped_lines.extend(wrap(line, max_x))

        num_lines = len(wrapped_lines)
        visible_lines = wrapped_lines[scroll_pos:scroll_pos + max_y]

        stdscr.clear()
        for i, line in enumerate(visible_lines):
            stdscr.addstr(i, 0, line[:max_x])

        stdscr.addstr(max_y, 0, f"Lines {scroll_pos + 1} - {scroll_pos + len(visible_lines)} of {num_lines}")
        stdscr.refresh()

        return num_lines
    else:
        print(message)