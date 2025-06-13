from .cross_sma_func import cross_sma
from .cross_ema_func import cross_ema

def get_strategy(name):
    if name == 'cross_sma':
        return cross_sma
    elif name == 'cross_ema':
        return cross_ema
    else:
        raise ValueError(f"Estrategia desconocida: {name}")
