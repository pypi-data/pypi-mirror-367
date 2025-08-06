#!/usr/bin/env python3
"""
TFCI (Time Forecasting CI) - 시계열 예측 라이브러리
"""

from .core.predictor import Predictor
from .config.config import load_config

def predict(config_path: str):
    """
    YAML 설정 파일로 시계열 예측 실행
    
    Args:
        config_path (str): 설정 파일 경로
        
    Returns:
        bool: 예측 성공 여부
    """
    config = load_config(config_path)
    predictor = Predictor(config)
    return predictor.run()

__version__ = "1.0.8"
__author__ = "TFCI Team"
__email__ = "rosci671233@gmail.com" 