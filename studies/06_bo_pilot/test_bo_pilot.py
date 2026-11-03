"""Checks for the adaptive-pilot engine. Run: python test_bo_pilot.py [--mongo-uri URI]

The MongoDB test needs a disposable server (the Makefile target starts one in a temp folder).
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from bo_pilot import (Config, Engine, MemoryStore, MongoStore, Posterior, best_share, learning_scores,
                      random_knobs, to_unit)
from simulate import play, run_launch


def test_best_share_matches_brute_force():
    cfg = Config()
    s = np.linspace(0.001, 0.999, 20001)
    for a in (0.2, 0.5, 0.75):
        ev = np.exp(cfg.delta) * s ** a + (1 - s) ** a
        assert abs(s[ev.argmax()] - best_share(cfg, a)) < 1e-3, a


def test_learning_score_matches_polyfit():
    cfg, rng = Config(), np.random.default_rng(0)
    sh = rng.uniform(0.05, 0.95, (50, 9))
    gap = np.abs(sh - best_share(cfg, 0.5))
    ref = np.array([-np.polyfit(np.arange(1, 10), g, 1)[0] * 8 * 100 for g in gap])
    assert np.allclose(learning_scores(cfg, sh, 0.5), ref)


def test_random_knobs_respect_ranges_and_time_cap():
    cfg = Config()
    s, a, r = random_knobs(cfg, np.random.default_rng(1), 5000)
    assert s.min() >= cfg.snr_range[0] and s.max() <= cfg.snr_range[1]
    assert a.min() >= cfg.alpha_range[0] and a.max() <= cfg.alpha_range[1]
    assert set(r) == set(range(cfg.rounds_range[0], cfg.max_rounds() + 1))


def test_gp_finds_known_peak():
    """Noisy draws from a known bump: the posterior-mean pick should land near the peak."""
    cfg, rng = Config(), np.random.default_rng(2)
    s, a, r = random_knobs(cfg, rng, 300)
    U = to_unit(cfg, s, a, r)
    peak = np.array([0.7, 0.3, 0.4])
    f = 30 * np.exp(-np.sum((U - peak) ** 2, axis=1) / 0.08)
    post = Posterior(cfg, U, f + rng.normal(0, 10, len(f)), 0)
    rec = post.recommend()
    u = to_unit(cfg, [rec["snr"]], [rec["alpha"]], [rec["rounds"]])[0]
    assert np.abs(u - peak).max() < 0.2, (u, peak)
    picks = post.thompson_index(rng, 200)
    assert len(set(picks)) > 5, "Thompson draws should not all pick the same setting"


def test_launch_policy():
    cfg = Config(n_max=120)
    store, _ = run_launch(cfg, seed=5)
    ps = sorted(store.all_participants(), key=lambda p: p["started_at"])
    assert len(ps) == cfg.n_max and len(store.completed()) == cfg.n_max
    assert all(p["kind"] == "warm-up random" for p in ps[:cfg.n_init])
    assert all(cfg.minutes(p["rounds"]) <= cfg.minutes_cap for p in ps)
    later = [p for p in ps if p["kind"] != "warm-up random"]
    share_random = np.mean([p["kind"] == "random" for p in later])
    assert 0.08 < share_random < 0.45, share_random
    ns = [s["n"] for s in store.get_snapshots()]
    assert ns[0] >= cfg.n_init and all(b - a >= cfg.refit_every for a, b in zip(ns, ns[1:])), ns
    # every Thompson assignment came from a GP fitted before the person arrived
    assert all(p["gp_version"] >= 1 for p in ps if p["kind"] == "thompson")


def test_mongo_store(uri):
    from pymongo import MongoClient
    db = "bo_pilot_test"
    MongoClient(uri).drop_database(db)
    cfg = Config(n_max=60, queue_size=25)
    store = MongoStore(uri, db)
    eng = Engine(cfg, store, rng=np.random.default_rng(3))
    eng.refill(0.0)
    assert store.queued_count() == 25
    # 25 people start at once: each must get a distinct assignment
    with ThreadPoolExecutor(10) as ex:
        got = list(ex.map(lambda i: store.claim(f"m{i:02d}", float(i)), range(25)))
    assert len({g["aid"] for g in got}) == 25
    rng = np.random.default_rng(4)
    for g in got:
        sh, rr, rd = play(cfg, g["snr"], g["alpha"], g["rounds"], rng)
        store.complete(g["pid"], sh[0], rr[0], rd[0], 100.0 + g["claimed_at"])
    assert eng.maybe_refit(200.0) is True
    assert store.get_meta()["gp_version"] == 1 and len(store.get_snapshots()) == 1
    assert store.queued_count() == 25
    # a fresh, stateless job rebuilds the same GP and keeps issuing Thompson draws
    eng2 = Engine(Config(n_max=60, queue_size=50), MongoStore(uri, db), rng=np.random.default_rng(5))
    eng2.load_posterior()
    assert eng2.post is not None and abs(eng2.post.mu.max() - eng.post.mu.max()) < 1e-6
    # the total cap holds: with 25 already issued and a 50-slot queue, only 35 more can be queued
    store.clear_queue()
    eng2.refill(300.0)
    assert store.queued_count() == 35
    MongoClient(uri).drop_database(db)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mongo-uri")
    args = ap.parse_args()
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_") and k != "test_mongo_store"]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    if args.mongo_uri:
        test_mongo_store(args.mongo_uri)
        print("ok  test_mongo_store")
    else:
        print("skip test_mongo_store (no --mongo-uri)")
    sys.exit(0)
