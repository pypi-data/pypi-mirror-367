import loguru
import requests
import time
import json

def request_trajectory(target_point, endpoint=None, max_retries=3):
    ...