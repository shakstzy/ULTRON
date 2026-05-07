---
type: paper
title: Attention Is All You Need
authors:
- ashish-vaswani
- noam-shazeer
- niki-parmar
- jakob-uszkoreit
- llion-jones
- aidan-gomez
- lukasz-kaiser
- illia-polosukhin
venue: null
year: 2017
arxiv_id: '1706.03762'
doi: null
source_url: https://arxiv.org/pdf/1706.03762v7
tags:
- ai-architecture
- machine-learning
- research-papers
- transformers
mentioned_concepts:
- self-attention
- multi-head-attention
- parallelization
- recurrent-neural-networks
- sequence-transduction
mentioned_books: []
slug: vaswani-attention-all-you-2017
read_status: ingested
delivered_at: null
delivery_count: 0
ingested_at: '2026-05-07'
last_touched: '2026-05-07'
bite_size_minutes: 2
---
## TL;DR

Turns out sequence models don't actually need complex recurrent or convolutional layers—just attention mechanisms. By ditching the sequential constraints of RNNs and going all-in on self-attention, you can process the whole sequence in parallel. It completely changes the game for training speed and model quality.

## Key takeaways

- Recurrent models are a bottleneck because they inherently process tokens sequentially—you can't batch compute effectively across a single long sequence due to memory constraints.
- Self-attention solves the "distant dependencies" problem by relating two arbitrary positions in a sequence using a constant number of operations, rather than a linear or logarithmic amount.
- Dropping recurrence entirely unlocks massive parallelization, meaning you can train state-of-the-art models in just a few days on a handful of GPUs.
- The only trade-off of relying purely on attention is a drop in "effective resolution," but patching it with "Multi-Head Attention" brings the nuance right back.

## Quote

"We propose a new simple network architecture, the Transformer, based solely on attention mechanisms" — Ashish Vaswani et al., Abstract

## Why it matters

Every LLM reshaping the tech landscape today is built on this exact architectural pivot. Grasping how ditching RNNs for pure attention enabled massive parallelization is foundational for understanding why current scaling laws even exist.

## Connections

_(none yet — populated as the corpus grows)_

## Backlinks

_(auto-built by `_shell/bin/build-backlinks.py`)_
