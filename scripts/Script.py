try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import transformers
    import torch
    import sqlalchemy
    import requests
    from fastapi import FastAPI
    print("All libraries imported successfully!")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")