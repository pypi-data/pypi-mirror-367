# experiments.py
from __future__ import annotations
import time
import numpy as np
import matplotlib.pyplot as plt

from .bandit import Bandit
from .utils import _compute_w_star
# If you defined these elsewhere, import them here:
from .utils import lower_bound, fixed_confidence_lower_bound

def run_experiment(
    env_path: str,
    algo_name: str,
    algo_args: dict,
    tracker_name: str | None,
    stopping_name: str | None,
    runs: int = 10,
    delta: float = 0.1,
    expected_best: int | None = None,
    show_plot: bool = False,
) -> dict:
    b = Bandit.from_saved_env(
        path=env_path,
        algo_name=algo_name,
        algo_args=algo_args,
        tracker_name=tracker_name,
        stopping_name=stopping_name,
    )

    env = b.env
    if hasattr(env, "probs"):
        mu = np.array(env.probs)
    elif hasattr(env, "mu"):
        mu = np.array(env.mu)
    else:
        raise ValueError("Unknown environment structure for extracting true means")

    T_star = lower_bound(mu, env=env)
    full_lb = fixed_confidence_lower_bound(mu, env=env, delta=delta)

    cumulative_hist = np.zeros_like(mu, dtype=float)
    pulls = 0
    tsum = 0.0
    wrong = 0
    max_pulls = 0
    last_history = None

    true_best = int(np.argmax(mu))
    check_against = true_best if expected_best is None else expected_best

    for i in range(runs):
        start = time.perf_counter()
        best, counts, rewards, history = b.run()
        elapsed = time.perf_counter() - start

        if best != check_against:
            wrong += 1
        total_pulls = int(counts.sum())
        pulls += total_pulls
        max_pulls = max(max_pulls, total_pulls)
        tsum += elapsed
        cumulative_hist += history[-1]
        last_history = history

    avg_hist = cumulative_hist / runs
    summary = {
        "T_star": T_star,
        "fixed_conf_lb": full_lb,
        "avg_pulls": pulls / runs,
        "max_pulls": max_pulls,
        "avg_time": tsum / runs,
        "wrong": wrong,
        "avg_last_hist": avg_hist,
    }

    if show_plot and last_history is not None:
        K = len(mu)
        times = np.arange(1, len(last_history) + 1)
        fig, ax = plt.subplots()
        for k in range(K):
            series = [h[k] for h in last_history]
            ax.plot(times, series, label=f"arm {k}", linewidth=1.5)
        w_star = _compute_w_star(mu, env=env)
        for k in range(K):
            ax.hlines(w_star[k], times[0], times[-1], linestyles="--", linewidth=1.0)
        ax.set_xlabel("Iteration (total pulls)")
        ax.set_ylabel("Empirical proportion")
        ax.legend(fontsize="small", bbox_to_anchor=(1.02, 1), loc="upper left")
        ax.grid(True)
        fig.tight_layout()
        plt.show()

    return summary
