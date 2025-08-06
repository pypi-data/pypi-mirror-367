# psm_analyzer.py

import numpy as np
from scipy.interpolate import interp1d
from typing import Optional, Dict, List


def find_intersection(y1: List[float], y2: List[float], x: np.ndarray) -> Optional[float]:
    """
    2つの曲線の交差点（x座標）を線形補間で求める。
    交差が見つからない場合は None を返す。
    """
    diff = np.array(y1) - np.array(y2)
    sign_change = np.where(np.diff(np.sign(diff)) != 0)[0]
    if len(sign_change) == 0:
        return None
    i = sign_change[0]
    try:
        f = interp1d(diff[i:i+2], x[i:i+2])
        return float(f(0))
    except Exception:
        return None


def calculate_psm(price_data: Dict[str, List[float]], step: int = 100) -> Dict[str, Optional[int]]:
    """
    Van Westendorp価格感度メーターに基づき、価格指標（OPP, IDP, PME, PMC）を計算する。

    Parameters:
        price_data: 以下の4キーを含む辞書
            - 'too_cheap': あまりにも安いと感じた価格
            - 'cheap': 安いと感じた価格
            - 'expensive': 高いと感じた価格
            - 'too_expensive': あまりにも高いと感じた価格
        step: 分析に使う価格ステップ幅（デフォルト100）

    Returns:
        各価格指標（OPP, IDP, PME, PMC）の辞書
    """
    all_valid_prices = [arr for arr in price_data.values() if len(arr) > 0]
    if not all_valid_prices:
        return {}

    all_prices = np.arange(
        min(np.concatenate(all_valid_prices)),
        max(np.concatenate(all_valid_prices)) + step,
        step
    )
    n = sum(len(arr) for arr in all_valid_prices)

    cumulative = {
        'too_cheap': [np.sum(price_data.get('too_cheap', []) >= p) / n for p in all_prices],
        'cheap': [np.sum(price_data.get('cheap', []) >= p) / n for p in all_prices],
        'expensive': [np.sum(price_data.get('expensive', []) <= p) / n for p in all_prices],
        'too_expensive': [np.sum(price_data.get('too_expensive', []) <= p) / n for p in all_prices],
    }

    opp = find_intersection(cumulative['cheap'], cumulative['expensive'], all_prices)
    idp = find_intersection(cumulative['too_cheap'], cumulative['too_expensive'], all_prices)
    pme = find_intersection(cumulative['cheap'], cumulative['too_expensive'], all_prices)
    pmc = find_intersection(cumulative['expensive'], cumulative['too_cheap'], all_prices)

    return {
        "OPP": round(opp) if opp is not None else None,
        "IDP": round(idp) if idp is not None else None,
        "PMC": round(pmc) if pmc is not None else None,
        "PME": round(pme) if pme is not None else None,
    }
