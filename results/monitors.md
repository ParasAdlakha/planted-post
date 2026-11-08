
## Table 4. Monitors with partial views (episode level; positive = at least one agent opened the key)

| Monitor | sees | TPR | FPR | FPR in post arms (hint/direct) | agent attribution (Jaccard, true positives) |
|---|---|---|---|---|---|
| gateway_paths | tool-call paths only | 1.00 (102) | 0.00 (193) | 0.00 (55) | 1.00 |
| outcome | submitted answers only | 0.87 (102) | 0.00 (193) | 0.00 (55) | 0.90 |
| words | reports + stated methods | 0.88 (102) | 0.01 (193) | 0.02 (55) | 0.93 |
| board_final | final /cache snapshot | 0.57 (102) | 0.30 (193) | 0.45 (55) | 0.14 |
| board_history | gateway log of /cache writes | 0.44 (102) | 0.20 (193) | 0.29 (55) | 0.07 |
| cot_25 | 25% of reasoning | 0.35 (102) | 0.00 (193) | 0.00 (55) | 0.61 |
| cot_50 | 50% of reasoning | 0.66 (102) | 0.00 (193) | 0.00 (55) | 0.82 |
| cot_100 | all reasoning | 0.89 (102) | 0.00 (193) | 0.00 (55) | 0.94 |

### By model family (TPR / FPR)

| Monitor | OpenAI | open-weight |
|---|---|---|
| outcome | 0.99 (67) / 0.00 (149) | 0.66 (35) / 0.00 (44) |
| words | 1.00 (67) / 0.01 (149) | 0.66 (35) / 0.02 (44) |
| board_final | 0.60 (67) / 0.34 (149) | 0.51 (35) / 0.18 (44) |
| cot_25 | 0.39 (67) / 0.00 (149) | 0.29 (35) / 0.00 (44) |
| cot_50 | 0.75 (67) / 0.00 (149) | 0.49 (35) / 0.00 (44) |
| cot_100 | 1.00 (67) / 0.00 (149) | 0.69 (35) / 0.00 (44) |

### Board monitors: false-positive rate by arm (episodes with no violation)

| Arm | board_final FPR | board_history FPR | n |
|---|---|---|---|
| none | 0.00 | 0.00 | 41 |
| benign | 0.00 | 0.00 | 33 |
| hint | 0.00 | 0.00 | 30 |
| direct | 1.00 | 0.64 | 25 |
| direct_c0 | 1.00 | 0.56 | 16 |
| direct_c1 | 1.00 | 0.85 | 13 |
| direct_c3 | 0.12 | 0.06 | 16 |
| direct_c3_warn | 0.11 | 0.11 | 19 |
