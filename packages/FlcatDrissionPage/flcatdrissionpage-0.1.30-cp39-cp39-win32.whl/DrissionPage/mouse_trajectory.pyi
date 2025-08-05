import loguru
import requests
import time
import json

def request_trajectory(target_point, endpoint='http://mouse-trajectory.flcat.top/infer', max_retries=3):
    """
    带重试机制的轨迹请求函数
    :param endpoint: 服务地址，例如 "http://mouse-trajectory.flcat.top/infer"
    :param target_point: 目标终点坐标，格式为 (x, y)
    :param max_retries: 最大重试次数（默认3次）
    :return: 请求结果字典 或 None
    """
    ...