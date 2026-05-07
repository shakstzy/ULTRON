---
type: youtube-video
title: But what is a neural network? | Deep learning chapter 1
video_id: aircAruvnKk
url: https://www.youtube.com/watch?v=aircAruvnKk
channel: 3blue1brown
channel_handle: '@3Blue1Brown'
authors:
- blue-brown
duration_minutes: 18
published_at: '2017-10-05'
tags:
- neural-networks
- machine-learning
- linear-algebra
- mental-models
mentioned_concepts:
- weights-and-biases
- sigmoid-function
- relu
- matrix-vector-multiplication
- hidden-layers
- activation-function
mentioned_books: []
slug: 3blue1brown-what-neural-network-deep
read_status: ingested
delivered_at: null
delivery_count: 0
ingested_at: '2026-05-07'
last_touched: '2026-05-07'
bite_size_minutes: 2
---
## TL;DR

A neural network is ultimately just a massively complex mathematical function with thousands of tweakable parameters that map inputs to outputs. By passing data through sequential layers of matrix multiplications, the network builds hierarchical abstractions—like grouping raw pixels into edges, and edges into distinct shapes—to recognize complex concepts.

## Key takeaways

- Neurons aren't magical; they're simply containers for a number (an activation) representing how strongly they've been triggered by the previous layer.
- Layering is how networks build abstraction: earlier layers detect simple subcomponents like little edges, while deeper layers combine those into recognizable loops, lines, and final concepts.
- Weights determine what specific pattern a neuron is listening for, while biases set the threshold for how strong that pattern needs to be before the neuron actually fires.
- The "learning" part of machine learning is literally just a computer systematically finding valid settings for thousands (or millions) of numeric knobs.
- Formulating network layers as linear algebra (matrix-vector multiplication) isn't just for clean notation—it's exactly what allows hardware to compute and optimize the math so incredibly fast.
- While the sigmoid function was the biologically-inspired default for squishing outputs, modern deep learning mostly uses ReLU (max(0, a)) because it's significantly easier to train.

## Quote

"Really the entire network is just a function." — 3Blue1Brown, Deep learning chapter 1

## Why it matters

Demystifying the "black box" of neural networks into basic linear algebra reveals that AI isn't magic—it's just highly optimized, scalable math. Stripping away the biological buzzwords makes it much easier to build a functional intuition for how state-of-the-art architectures actually work under the hood.

## Connections

_(none yet — populated as the corpus grows)_

## Backlinks

_(auto-built by `_shell/bin/build-backlinks.py`)_
