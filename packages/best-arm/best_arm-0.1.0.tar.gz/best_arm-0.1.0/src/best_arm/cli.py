import argparse
import json
import numpy as np
from .experiments import run_experiment

def main():
    p = argparse.ArgumentParser(prog="multi-arm", description="Run multi-armed bandit experiments.")
    p.add_argument("--env", required=True, help="Path to a saved environment JSON (e.g., env_0002.json)")
    p.add_argument("--algo", required=True, help="Algorithm name (see ALGO_REGISTRY)")
    p.add_argument("--algo-args", default="{}", help='JSON dict, e.g. {"confidence":0.1}')
    p.add_argument("--tracker", default=None, help="Tracker name or None")
    p.add_argument("--stopping", default=None, help="Stopping condition name or None")
    p.add_argument("--runs", type=int, default=10)
    p.add_argument("--delta", type=float, default=0.1)
    p.add_argument("--expected-best", type=int, default=None)
    p.add_argument("--show-plot", action="store_true")

    args = p.parse_args()
    try:
        algo_args = json.loads(args.algo_args)
        if not isinstance(algo_args, dict):
            raise ValueError
    except Exception:
        raise SystemExit("--algo-args must be a JSON object, e.g. '{\"confidence\":0.1}'")

    summary = run_experiment(
        env_path=args.env,
        algo_name=args.algo,
        algo_args=algo_args,
        tracker_name=args.tracker,
        stopping_name=args.stopping,
        runs=args.runs,
        delta=args.delta,
        expected_best=args.expected_best,
        show_plot=bool(args.show_plot),
    )

    # Pretty print numeric arrays
    def _fmt(x):
        if isinstance(x, np.ndarray):
            return x.tolist()
        return x

    print(json.dumps({k: _fmt(v) for k, v in summary.items()}, indent=2))
