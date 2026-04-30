---
slug: kronos
type: concept
canonical_name: Kronos
domain: quant-research
research_date: 2026-04-30
---

# Kronos — Foundation Model for K-line Forecasting

> Research note. Not a recommendation to trade.

## What it is

- Repo: [shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos) — 22,266 stars, 3,920 forks, MIT license, last push 2026-04-13.
- Paper: [arXiv 2508.02739](https://arxiv.org/abs/2508.02739). Accepted to AAAI 2026.
- Author: Shiyu (PhD researcher).
- HuggingFace org: [NeoQuasar](https://huggingface.co/NeoQuasar).
- Live demo: [shiyu-coder.github.io/Kronos-demo](https://shiyu-coder.github.io/Kronos-demo/) — forecasts BTC/USDT 24h ahead.

### Architecture

Decoder-only transformer. Two stage:
1. Tokenizer quantizes OHLCV bars into hierarchical discrete tokens.
2. Autoregressive transformer predicts next tokens.

### Pretraining corpus

- 12B+ K-line records.
- 45 global exchanges.
- 7 granularities (5m through daily).
- Cutoff: through June 2024 per paper. Public test starts July 2024.
- **Open issue: no exact training-date cutoff in the README/model card. Researchers asking for it in [issue #265](https://github.com/shiyu-coder/Kronos/issues/265). Without this, US-equity OOS results may report memorization as skill.**

### Released models

| Model | Params | Context | Open |
|---|---|---|---|
| Kronos-mini | 4.1M | 2048 | Yes |
| Kronos-small | 24.7M | 512 | Yes |
| Kronos-base | 102.3M | 512 | Yes |
| Kronos-large | 499.2M | 512 | **No** (not released) |

Default usage: `lookback=400`, `pred_len=120`. Daily simulation in paper: 90 lookback, 10 horizon.

## Evidence of live effectiveness

**No audited broker statements. No third-party verified live PnL. No public live tracker.**

What exists:
- First-party Qlib backtest on Chinese A-shares (long-only top-K) in the paper, with transaction-cost assumptions.
- Strong RankIC numbers in-sample/in-paper.
- Heavy GitHub-stars momentum, viral on X/Twitter.

What does NOT exist after a deep search across X, Reddit (r/algotrading, r/quant, r/MachineLearning), HackerNews, YouTube, blogs:
- A single broker-statement screenshot tied to Kronos.
- A third-party live track-record longer than days.
- Audited / reproducible PnL.

### Independent third-party benchmark — devastating

[Issue #269](https://github.com/shiyu-coder/Kronos/issues/269): user ran Kronos-base on 200 ETFs vs a HistVol20 baseline. Kronos lost across the board:

| Metric (H=10) | Kronos | HistVol20 | Verdict |
|---|---|---|---|
| CRPS | 0.127 | 0.040 | 3.1x worse |
| Cover90 | 0.25 | 0.86 | severely under-dispersed |
| RMSE close | 0.157 | 0.074 | 2.1x worse |
| Direction acc | 0.49 | 0.51 | both coin-flip |
| PIT KS | 0.53 | 0.11 | calibration broken |

Quote from a commenter: "Kronos pretraining used future data, which already shows the training is invalid. The actual application has no predictive ability." This is a single test on ETFs, not the full Chinese-A-share use case the paper targets, but it is the only public independent test and it failed.

### Open data-leakage finding

[PR #263](https://github.com/shiyu-coder/Kronos/pull/263) — open, NOT merged as of 2026-04-30. A contributor flagged that `CustomKlineDataset.__getitem__` in the fine-tune pipeline computes mean/std over the FULL window including the prediction-target period, leaking future statistics into features. A clean fix is sitting unmerged. If you fine-tune on your own data without this patch, your backtest is corrupted.

### README's own disclaimer

> "This pipeline is intended as a demonstration to illustrate the finetuning process. It is a simplified example and not a production-ready quantitative trading system."

The author themselves says it's not production-ready.

## Strategies people layer on top

Kronos emits forecast price paths. It is NOT a trading system. Strategies that pair with a generic forecast model:

| Asset class | Setup | Notes |
|---|---|---|
| Spot equities (cross-section) | Long-top-K / short-bottom-K from Kronos rank | What the paper tests on Chinese A-shares. Cleanest published evidence, but only first-party. |
| Crypto perps | Directional with vol-targeting | High retail-noise, easier signal, also easier to blow up on funding/leverage. |
| CME index futures | Ensemble feature into a momentum/mean-reversion overlay | Liquid, low fees, good for risk-controlled deployment. |
| Options (delta-neutral) | Vol-rank / IV-rank gating, not direction bets | Defensible: use the forecast for IV regime, not for picking calls vs puts. |
| Pairs / stat-arb | Use forecast residuals on cointegrated pairs | Lower exposure to single-asset overfit. |

Cleanest signal in independent tests: **none confirmed.** First-party paper points to A-share cross-section. The one independent ETF test failed.

## Risk management — required regardless

If anyone deploys this, the risk wrapper is more important than the model:

- **Hard portfolio drawdown circuit breaker.** Stop trading when peak-to-trough hits the cap (e.g. 15% halt to paper, 20% halt entirely).
- **Vol-targeted position sizing.** Each position scaled to a constant vol contribution (e.g. annualized 10% per leg).
- **Fractional Kelly, hard-capped.** Quarter or eighth Kelly. Never full Kelly on a forecast model with unknown true edge.
- **Per-asset hard stops.** Time-stop and price-stop on every leg.
- **Diversification across uncorrelated signals.** Kronos is one signal, not the portfolio.
- **Liquidity and slippage filters.** ADV-based caps, bid-ask realism in backtests, fees modeled.
- **Walk-forward retraining.** Refresh fine-tune on a rolling window that ENDS before the eval window starts. Read PR #263 first.
- **Paper / shadow trade for 60-90 days minimum.** Compare live forecasts to realized prices before risking size. If realized error or calibration drifts past threshold, kill switch.
- **Regime detection.** If 2026 macro regime drifts past pretraining distribution (shift in vol clusters, correlation breakdown), reduce or stop.

## Red flags / failure modes

1. Training-data temporal cutoff is unclear. US-equity OOS results may be memorization.
2. PR #263 leakage fix unmerged. Fine-tune backtests on the official pipeline are suspect.
3. One independent test (#269) on 200 ETFs LOST to a 20-day historical-vol baseline.
4. Forecast distributions are under-dispersed (Cover90 = 0.25 vs target 0.90). Probabilistic claims unreliable.
5. Direction accuracy 0.49 in the independent test = coin-flip = no usable directional edge in that asset class.
6. Viral X/Twitter "20% in a week" claims are unverified. None tied to broker statements.
7. Kronos-large (499M params, biggest model) is NOT open. Public users can only access the smaller checkpoints.
8. Microcap / illiquid pump bias possible if naive backtests don't filter ADV.
9. 2026 macro regime drift since the June 2024 pretraining cutoff.
10. Visually plausible candle generations are not the same as executable alpha.

## Reality check

Kronos is a legitimate research artifact (AAAI 2026 paper, real architecture, real code). It is NOT a money-printer. The viral "turns traders profitable" framing is not supported by any audited evidence as of 2026-04-30. The one available independent benchmark shows it loses to a trivial baseline on direction, calibration, and even point-error metrics. The author themselves disclaims production use.

Treat it as: an experimental signal generator, useful as one feature in an ensemble, with rigorous risk wrap and shadow-trading before any real money.

## Defensible deployment if you must

If you decide to use Kronos with a 15-20% hard max drawdown cap:

1. **Patch first.** Apply PR #263's normalization fix locally. Otherwise fine-tune backtests are leaking.
2. **Pick liquid universe.** SP500, Nasdaq 100, top 30 crypto by ADV. Skip microcaps.
3. **Fine-tune on post-cutoff data only.** July 2024 onward. Fully walk-forward.
4. **Ensemble, never solo.** Kronos + 1-2 classical signals (cross-sectional momentum, residual-reversion). Equal-weight or risk-weight the signals.
5. **Vol-target each leg** to ~10% annualized, total portfolio ~12% annualized.
6. **Hard portfolio kill switch at 15% drawdown.** No averaging down. No "it'll come back."
7. **Shadow trade 60-90 days.** Compare live forecasts to realized prices. Track calibration, not just PnL.
8. **Quarter Kelly, capped.** Cap any single position at 5% of NAV.
9. **No options, no leveraged products initially.** Spot or 1x perp only until shadow track exists.
10. **Quarterly re-fit, monthly performance review.** Pull plug if calibration or hit-rate degrades two consecutive months.

## Sources

- Repo: [github.com/shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos)
- Paper: [arxiv.org/abs/2508.02739](https://arxiv.org/abs/2508.02739)
- HF: [huggingface.co/NeoQuasar](https://huggingface.co/NeoQuasar)
- ETF benchmark: [issue #269](https://github.com/shiyu-coder/Kronos/issues/269)
- Cutoff transparency request: [issue #265](https://github.com/shiyu-coder/Kronos/issues/265)
- Leakage fix unmerged: [PR #263](https://github.com/shiyu-coder/Kronos/pull/263)
- Cross-checked via Codex live web search (2026-04-30).
