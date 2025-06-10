# src/monkeypatch_numpy.py
import numpy as _np

# Asegura que numpy.NaN exista para compatibilidad con pandas-ta
setattr(_np, "NaN", _np.nan)
