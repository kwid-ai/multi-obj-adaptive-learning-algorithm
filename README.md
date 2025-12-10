<h1 align="center"><br><sub><sup>A Multi-Objective Adaptive Learning Algorithm: A Synthesis of Pedagogical Models</sup></sub></h1>

<div align="center" style="line-height: 1;">
    <a href='https://'><img src='https://img.shields.io/badge/Technical Report-PDF-red'></a>
</div>

# Adaptive Learning Optimization Framework
This repository contains the novel adaptive algorithm that formulates personalization as a Multi-Objective Optimization (MOO) problem, instead of optimizing for a single metric (like test score), it seeks to balance multiple, often conflicting, objectives to achieve a holistic and effective learning experience. The model explicitly integrates (i) knowledge gap targeting, (ii) cognitive load optimization, (iii) learning style alignment, (iv) engagement prediction, and (v) exploration bonuses, while imposing pedagogical constraints to maintain educational integrity.
![image](adaptive%20algorithm.png)

Adaptive Learning to select the optimal content $C^*$ is defined as:
```math
C^* = \arg\max_{c \in C} \Bigg[
    w_{ls} \cdot LS(c,st) \;+\;
    w_{d} \cdot D(c,st) \;+\;
    w_{cl} \cdot CL(c,st) \;+\;
    w_{kg} \cdot KG(c,st) \;+\; \\
     w_{e} \cdot Eng(c, st)  \;+\;
    \beta \cdot \sqrt{\frac{\ln(N)}{N_c}}
```


The system dynamically selects optimal educational content by solving a real-time optimization problem, maximizing a weighted scoring function that synthesizes five key components:

- Bayesian Knowledge Tracing (BKT): For probabilistic knowledge estimation.

- Zone of Proximal Development (ZPD): For difficulty targeting.

- Cognitive Load Theory (CLT): For state-aware instructional design.

- Learning Style Matching: For personalized content modality.

- Upper Confidence Bound (UCB) Exploration: For handling the explore-exploit trade-off.

Key Features: Highly personalized content delivery, real-time student state modeling (knowledge, style, load), and dynamic policy adjustment.

# Reference

Cite the algorithm as "Multi-Objective Adaptive Learning Algorithm".

	@article{komolafe-code-2025,    
		  author    = {Oyindolapo Komolafe},
		  title     = {Multi-Objective Adaptive Learning Algorithm},
		  journal   = {}, 
		  volume    = {},
  		  number    = {1},
     	  pages     = { },
  		  year      = {2025},
  	      url       = {}
	}     
