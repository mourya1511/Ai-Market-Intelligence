# src/confidence.py
import numpy as np
from scipy import stats

def cohen_d(a, b):
    a = np.array(a); b = np.array(b)
    na, nb = len(a), len(b)
    if na<2 or nb<2:
        return 0.0
    pooled_sd = np.sqrt(((na-1)*a.std(ddof=1)**2 + (nb-1)*b.std(ddof=1)**2) / (na+nb-2))
    if pooled_sd == 0: return 0.0
    return (a.mean() - b.mean()) / pooled_sd

def compute_confidence(n, p_value, effect_size, freshness_days):
    # n: sample size contributing to insight
    # p_value: statistical p-value (smaller => stronger)
    # effect_size: absolute effect (Cohen's d)
    # freshness_days: recency (smaller => fresher)
    # produce 0..1 score
    n_score = 1 - np.exp(-n/100)      # saturates ~1 for n>400
    p_score = 1 - min(1, max(0, -np.log10(p_value+1e-12)/6))  # p=1e-6 => high score
    e_score = 1 - np.exp(-abs(effect_size)/0.5)  # 0.5 is meaningful
    freshness_score = np.exp(-freshness_days/365)  # 1 year halves ~0.37
    # weighted
    w = { 'n':0.25, 'p':0.25, 'e':0.3, 'f':0.2 }
    score = w['n']*n_score + w['p']*p_score + w['e']*e_score + w['f']*freshness_score
    return float(round(score,3))
