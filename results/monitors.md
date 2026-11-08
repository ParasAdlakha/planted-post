
## Table 4. Monitors with partial views (episode level; positive = at least one agent opened the key)

| Monitor | sees | TPR | FPR | FPR in post arms (hint/direct) | agent attribution (Jaccard, true positives) |
|---|---|---|---|---|---|
| gateway_paths | tool-call paths only | 1.00 (91) | 0.00 (189) | 0.00 (52) | 1.00 |
| outcome | submitted answers only | 0.88 (91) | 0.00 (189) | 0.00 (52) | 0.93 |
| words | reports + stated methods | 0.89 (91) | 0.01 (189) | 0.02 (52) | 0.95 |
| board_final | final /cache snapshot | 0.63 (91) | 0.29 (189) | 0.42 (52) | 0.13 |
| board_history | gateway log of /cache writes | 0.47 (91) | 0.20 (189) | 0.29 (52) | 0.06 |
| cot_25 | 25% of reasoning | 0.35 (91) | 0.00 (189) | 0.00 (52) | 0.66 |
| cot_50 | 50% of reasoning | 0.66 (91) | 0.00 (189) | 0.00 (52) | 0.84 |
| cot_100 | all reasoning | 0.90 (91) | 0.00 (189) | 0.00 (52) | 0.96 |

### By model family (TPR / FPR)

| Monitor | OpenAI | open-weight |
|---|---|---|
| outcome | 0.99 (67) / 0.00 (149) | 0.58 (24) / 0.00 (40) |
| words | 1.00 (67) / 0.01 (149) | 0.58 (24) / 0.03 (40) |
| board_final | 0.60 (67) / 0.34 (149) | 0.71 (24) / 0.12 (40) |
| cot_25 | 0.39 (67) / 0.00 (149) | 0.25 (24) / 0.00 (40) |
| cot_50 | 0.75 (67) / 0.00 (149) | 0.42 (24) / 0.00 (40) |
| cot_100 | 1.00 (67) / 0.00 (149) | 0.62 (24) / 0.00 (40) |

### Board monitors: false-positive rate by arm (episodes with no violation)

| Arm | board_final FPR | board_history FPR | n |
|---|---|---|---|
| none | 0.00 | 0.00 | 41 |
| benign | 0.00 | 0.00 | 33 |
| hint | 0.00 | 0.00 | 30 |
| direct | 1.00 | 0.68 | 22 |
| direct_c0 | 1.00 | 0.56 | 16 |
| direct_c1 | 1.00 | 0.85 | 13 |
| direct_c3 | 0.12 | 0.06 | 16 |
| direct_c3_warn | 0.11 | 0.11 | 18 |
