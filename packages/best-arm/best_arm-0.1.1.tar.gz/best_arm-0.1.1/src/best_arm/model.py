# model.py

from typing import Type, Dict, Optional

from .environment import BaseEnvironment

class BaseTracker:
    def __init__(self, num_arms: int, **kwargs):
        self.num_arms = num_arms

    def select_arm(self, counts, rewards, env: BaseEnvironment):
        raise NotImplementedError

class BaseAlgorithm:
    def __init__(
        self,
        env: BaseEnvironment,
        confidence: float,
        tracker: Optional[BaseTracker] = None,
        **kwargs
    ):
        self.env = env
        self.confidence = confidence
        self.tracker = tracker

    def run(self):
        raise NotImplementedError


from .algorithms.exp_gap_elim import ExpGapElimination
from .algorithms.lil_ucb import LilUCB
from .algorithms.lucb1 import LUCB1
from .algorithms.gradient_ascent import GradientAscent

from .algorithms.track_and_stop import (
    CTracking, DTracking, HeuristicTracking, GTracking,
    DOracleTracking, RealOracleTracking, TrackAndStop, BestChallengerTracking, OptimisticTracking, NoisyTracking
)
from .algorithms.track_and_stop import SamplingTracking
from .algorithms.frank_wolfe import FWS
from .algorithms.top_two import TopTwoBAI
from .algorithms.adahedge import AdaHedgeBestResponse
TRACKER_REGISTRY: Dict[str, Type[BaseTracker]] = {
    "c_tracking":            CTracking,
    "d_tracking":            DTracking,
    "heuristic_tracking":    HeuristicTracking,
    "g_tracking":            GTracking,
    "d_oracle_tracking":     DOracleTracking,
    "real_oracle_tracking":  RealOracleTracking,
    "sampling_tracking": SamplingTracking,
    "bc": BestChallengerTracking,
    "optimistic_tracking" : OptimisticTracking,
    "noisy_tracking" : NoisyTracking
}

ALGO_REGISTRY: Dict[str, Type[BaseAlgorithm]] = {
    "track_and_stop":   TrackAndStop,
    "exp_gap_elim":     ExpGapElimination,
    "lil_ucb":          LilUCB,
    "lucb":             LUCB1,
    "lazyma":  GradientAscent,
    "fws": FWS,
    "top_two": TopTwoBAI,
    "adahedge_br": AdaHedgeBestResponse,
}

