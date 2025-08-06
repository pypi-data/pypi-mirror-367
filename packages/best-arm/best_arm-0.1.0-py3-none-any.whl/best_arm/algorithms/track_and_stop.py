# track_and_stop.py
import math
import numpy as np
from typing import Tuple, List
from ..environment import BaseEnvironment
from ..stopping_conditions import BaseStoppingCondition
from ..utils import _kl_bernoulli, _kl_gaussian, _compute_w_star, optimistic_oracle
from ..model import BaseTracker, BaseAlgorithm
def _project_simplex(v: np.ndarray) -> np.ndarray:
    u = np.sort(v)[::-1]
    cssv = np.cumsum(u)
    rho_candidates = u - (cssv - 1) / (np.arange(1, len(v) + 1))
    rho = np.where(rho_candidates > 0)[0].max()
    theta = (cssv[rho] - 1) / (rho + 1)
    return np.maximum(v - theta, 0.0)

class SamplingTracking(BaseTracker):
    def select_arm(
        self,
        counts: np.ndarray,
        rewards: np.ndarray,
        env: BaseEnvironment
    ) -> int:
        t = int(counts.sum()) + 1
        K = self.num_arms
        m = t // K
        if m >= 0 and int(math.isqrt(m)) ** 2 == m:
            return int(np.random.randint(K))
        mu_hat = rewards / np.maximum(counts, 1)
        w_star = _compute_w_star(mu_hat, env=env)
        v = t * w_star - counts
        pi = _project_simplex(v)
        return int(np.random.choice(self.num_arms, p=pi))
class CTracking(BaseTracker):
    def __init__(self, num_arms: int):
        super().__init__(num_arms)
        self.K = num_arms
        self.t = num_arms                   # Because of the first exploration
        self.cum_w = np.zeros(self.K, dtype=float)

    def select_arm(
        self,
        counts: np.ndarray,
        rewards: np.ndarray,
        env: BaseEnvironment
    ) -> int:
        # 1) increment time
        self.t += 1

        # 2) empirical means
        mu_hat = rewards / np.maximum(1, counts)

        # 3) compute ideal w*
        w_star = _compute_w_star(mu_hat, env=env)

        # 4) projection parameter
        eps_t = 0.5 / math.sqrt(self.K**2 + self.t)

        # 5) project and renormalize
        w_eps = np.clip(w_star, eps_t, None)
        w_eps /= w_eps.sum()

        # 6) accumulate
        self.cum_w += w_eps

        # 7) choose arm maximizing (cumulated weight − empirical pulls)
        scores = self.cum_w - counts
        return int(np.argmax(scores))

class DTracking(BaseTracker):
    def select_arm(self, counts, rewards, env: BaseEnvironment) -> int:
        t = int(counts.sum()) + 1
        if t == 0:
            return np.random.randint(self.num_arms)
        thresh = math.sqrt(t) - self.num_arms / 2.0
        under = [a for a in range(self.num_arms) if counts[a] < thresh]
        if under:
            return int(min(under, key=lambda a: counts[a]))
        mu_hat = rewards / np.maximum(1, counts)
        w_star = _compute_w_star(mu_hat, env=env)
        return int(np.argmax(t * w_star - counts))


class OptimisticTracking(BaseTracker):
    def select_arm(self, counts: np.ndarray, rewards: np.ndarray, env: BaseEnvironment) -> int:
        t = int(counts.sum()) + 1

        mu_hat = rewards / np.maximum(counts, 1)
        w_star = optimistic_oracle(mu_hat, counts, env)

        # Select the arm with the biggest gap between desired and current allocation
        allocation_gaps = t * w_star - counts
        return int(np.argmax(allocation_gaps))



class HeuristicTracking(BaseTracker):

    def select_arm(self, counts, rewards, env):
        t = int(counts.sum())
        K = self.num_arms

        if t > 0 and t % K == 0:
            return int(np.random.randint(K))


        mu_hat = rewards / np.maximum(1, counts)
        w_star = _compute_w_star(mu_hat, env=env)

        return int(np.random.choice(K, p=w_star))
class GTracking(BaseTracker):

    def select_arm(self, counts, rewards, env: BaseEnvironment) -> int:
        t = int(counts.sum())
        K = self.num_arms

        if t > 0 and t % K == 0:
            return int(np.random.randint(K))

        mu_hat = rewards / np.maximum(1, counts)
        w_star = _compute_w_star(mu_hat, env=env)

        p = counts / t

        d = w_star - p
        mask = d < 0
        if np.any(mask):
            alphas = p[mask] / (p[mask] - w_star[mask])
            alpha_max = np.min(alphas)
        else:
            alpha_max = 1.0

        x = p + alpha_max * d

        x = np.clip(x, 0.0, None)
        x = x / x.sum()

        return int(np.random.choice(K, p=x))

class DOracleTracking(BaseTracker):
    def __init__(self, num_arms: int):
        super().__init__(num_arms)
        self._w_star = None

    def select_arm(self, counts, rewards, env: BaseEnvironment) -> int:
        t = int(counts.sum()) + 1
        K = self.num_arms
        if t == 0:
            return np.random.randint(K)

        thresh = math.sqrt(t) - K / 2.0
        under = [a for a in range(K) if counts[a] < thresh]
        if under:
            return int(min(under, key=lambda a: counts[a]))

        if self._w_star is None:
            if hasattr(env, "mu"):
                mu = np.asarray(env.mu, dtype=float)
            else:
                mu = np.asarray(env.probs, dtype=float)
            self._w_star = _compute_w_star(mu, env=env)

        return int(np.argmax(t * self._w_star - counts))

class RealOracleTracking(BaseTracker):

    def __init__(self, num_arms: int):
        super().__init__(num_arms)
        self._w_star = None

    def select_arm(self, counts, rewards, env: BaseEnvironment) -> int:
        t = int(counts.sum()) + 1
        K = self.num_arms
        m = t // K
        if m >= 0 and int(math.isqrt(m)) ** 2 == m:
            return int(np.random.randint(K))
        if self._w_star is None:
            if hasattr(env, "mu"):
                mu = np.asarray(env.mu, dtype=float)
            else:
                mu = np.asarray(env.probs, dtype=float)
            self._w_star = _compute_w_star(mu, env=env)
        return int(np.random.choice(self.num_arms, p=self._w_star))


class BestChallengerTracking(BaseTracker):
    """
    After t pulls, let âₜ = argmax mû, and ĉₜ be the 'best challenger' minimizing
    the pairwise log‑likelihood ratio Z_{âₜ, c}(t). Then pull âₜ if
      N_{âₜ}/(N_{âₜ}+N_{ĉₜ}) < w*_{âₜ}/(w*_{âₜ}+w*_{ĉₜ}),
    else pull ĉₜ.  Forced exploration as in D‑Tracking.
    """
    def select_arm(self, counts: np.ndarray, rewards: np.ndarray, env: BaseEnvironment) -> int:
        t = int(counts.sum()) + 1
        K = self.num_arms

        # 1) forced exploration (same as D‑Tracking)
        thresh = math.sqrt(t) - K / 2.0
        under = [a for a in range(K) if counts[a] < thresh]
        if under:
            return int(min(under, key=lambda a: counts[a]))

        # 2) empirical means
        mu_hat = rewards / np.maximum(1, counts)

        # 3) champion âₜ
        a_hat = int(np.argmax(mu_hat))

        # 4) best challenger ĉₜ via pairwise Z-statistic
        def kl(p, q):
            # choose appropriate divergence
            if env.__class__.__name__.lower().startswith("normal"):
                return _kl_gaussian(p, q, sigma2=env.sigma**2)
            else:
                return _kl_bernoulli(p, q)

        def Z(i, j):
            ni, nj = counts[i], counts[j]
            # mixture mean
            m = (ni * mu_hat[i] + nj * mu_hat[j]) / (ni + nj)
            return ni * kl(mu_hat[i], m) + nj * kl(mu_hat[j], m)

        # find challenger
        cands = [c for c in range(K) if c != a_hat]
        c_hat = int(min(cands, key=lambda c: Z(a_hat, c)))

        # 5) compute w* for all arms
        w_star = _compute_w_star(mu_hat, env=env)

        # 6) decision rule
        left  = counts[a_hat] / (counts[a_hat] + counts[c_hat])
        right = w_star[a_hat] / (w_star[a_hat] + w_star[c_hat])
        return a_hat if left < right else c_hat

class NoisyTracking(BaseTracker):
    def __init__(self, num_arms: int, initial_variance: float = 4, min_variance: float = 1e-8):
        super().__init__(num_arms)
        self.initial_variance = initial_variance
        self.min_variance = min_variance

    def select_arm(self, counts, rewards, env: BaseEnvironment) -> int:
        t = int(counts.sum()) + 1  # as in DTracking
        K = self.num_arms

        # forced exploration like DTracking
        thresh = math.sqrt(t) - K / 2.0
        under = [a for a in range(K) if counts[a] < thresh]
        if under:
            return int(min(under, key=lambda a: counts[a]))

        # empirical means
        mu_hat = rewards / np.maximum(1, counts)

        # compute decaying variance
        var = max(self.initial_variance / (t), self.min_variance)

        # add zero-mean Gaussian noise
        noisy_mu = mu_hat + np.random.randn(K) * var

        # clip if Bernoulli (to [0,1]); leave as-is for Normal
        if not env.__class__.__name__.lower().startswith("normal"):
            noisy_mu = np.clip(noisy_mu, 0.0, 1.0)

        # get w* on noisy means
        w_star = _compute_w_star(noisy_mu, env=env)

        # same selection as DTracking: argmax of t * w_star - counts
        return int(np.argmax(t * w_star - counts))
class TrackAndStop(BaseAlgorithm):
    def __init__(
        self,
        env: BaseEnvironment,
        confidence: float,
        tracker: BaseTracker,
        stopping_condition: BaseStoppingCondition
    ):
        super().__init__(env=env, confidence=confidence, tracker=tracker)
        self.stopping_condition = stopping_condition

    def run(self) -> Tuple[int, np.ndarray, np.ndarray, List[np.ndarray]]:
        K = self.env.num_arms
        counts  = np.zeros(K, dtype=int)
        rewards = np.zeros(K, dtype=float)
        history: List[np.ndarray] = []

        for a in range(K):
            r = self.env.sample(a)
            counts[a] += 1
            rewards[a] += r
        history.append(counts / counts.sum())

        # 2) main loop
        while not self.stopping_condition.should_stop(
            counts, rewards, self.env, self.confidence
        ):
            arm = self.tracker.select_arm(counts, rewards, self.env)
            r = self.env.sample(arm)
            counts[arm] += 1
            rewards[arm] += r
            history.append(counts / counts.sum())

        best = int(np.argmax(rewards / counts))
        return best, counts, rewards, history

    def run_fixed(self, horizon: int) -> np.ndarray:
        """
        Run for exactly `horizon` total pulls, ignoring the stopping rule,
        and return an array `worsts` of length `horizon` where worsts[t-1]
        is the Chernoff statistic at pull t (or NaN if t < K).
        """
        K = self.env.num_arms
        counts = np.zeros(K, dtype=int)
        rewards = np.zeros(K, dtype=float)
        worsts = np.full(horizon, np.nan, dtype=float)

        # 1) initial K pulls
        for a in range(K):
            r = self.env.sample(a)
            counts[a] += 1
            rewards[a] += r
            t = int(counts.sum())
            if t <= horizon:
                worsts[t - 1] = self.stopping_condition.compute_statistic(
                    counts, rewards, self.env
                )

        # 2) next pulls up to horizon
        for t in range(K + 1, horizon + 1):
            arm = self.tracker.select_arm(counts, rewards, self.env)
            r = self.env.sample(arm)
            counts[arm] += 1
            rewards[arm] += r
            worsts[t - 1] = self.stopping_condition.compute_statistic(
                counts, rewards, self.env
            )

        return worsts