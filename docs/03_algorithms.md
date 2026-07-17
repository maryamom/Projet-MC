# 03 — Algorithms

This doc specifies what to implement and how to compare them.

---

## 1) UCT (baseline MCTS)

### MCTS loop (one iteration)
1. **Selection**: descend from root using UCB/UCT on children
2. **Expansion**: add one new child from an untried move
3. **Simulation**: run a playout from the expanded node to terminal
4. **Backpropagation**: update visit counts and wins along the path

### UCT selection (for node s, action a)
Let:
- N(s) = visits of node s
- N(s,a) = visits of child after action a
- Q(s,a) = mean value (e.g., winrate for current player)

Then choose:
```
argmax_a  Q(s,a) + C * sqrt( ln N(s) / N(s,a) )
```
C is exploration constant (typical 0.7–1.4; tune).

### Value convention
Pick one convention and stick to it:
- Store value from **root player’s perspective**, or
- Store value from **player-to-move** perspective

Avoid mixing conventions across algorithms.

---

## 2) AMAF / RAVE

### AMAF intuition
“All Moves As First”: if a move appears later in a playout, treat it as evidence for that move.

### Required statistics per node
For each move `m` in the move-space:
- AMAF_N[m] = # of playouts where `m` appeared (after this node)
- AMAF_W[m] = # of those playouts that ended in win (for the chosen perspective)

### RAVE blended value
For child move a:
- Q_uct = W(s,a)/N(s,a)
- Q_amaf = AMAF_W[a]/AMAF_N[a]
- Blend with β(N):
```
Q_rave = (1-β) * Q_uct + β * Q_amaf
```
β should decrease as N(s,a) increases.

### Practical β choice (simple)
A common course-style choice:
```
β = k / (N(s,a) + k)
```
Where k is a hyperparameter (e.g., 300–10000 depending on budget).

### Selection with RAVE
Use `Q_rave` inside the UCT formula:
```
Q_rave + C * sqrt( ln N(s) / N(s,a) )
```

### Backprop update
During backprop, also update AMAF stats for all moves in the playout that are legal from each visited node (careful: typically update for moves played after that node in the simulation).

---

## 3) GRAVE

### Idea
Instead of always using the current node’s AMAF stats, use AMAF stats from an ancestor that has enough visits (more reliable).

### Parameter
- Threshold `T`: minimal visits for a node to be considered “reliable” for AMAF.

### Algorithm sketch
At a node s:
- find the nearest ancestor `u` on the path with `N(u) ≥ T`
- use AMAF stats from `u` in the RAVE blend for selection at s

This often stabilizes early estimates and improves small-budget performance.

---

## 4) (Optional) PUCT (AlphaZero-style MCTS)

PUCT uses:
- A **prior policy** P(s,a) over moves (from a “network”)
- A **value** V(s) estimate (from the same network) to replace full playouts

### Selection rule
For each action a:
```
score(a) = Q(s,a) + c_puct * P(s,a) * sqrt(N(s)) / (1 + N(s,a))
```
Choose action with max score.

### Toy “network” options (no deep learning needed)
You can implement a function that returns:
- **Policy priors** P(s,a): e.g., softmax of a heuristic score, or uniform random, or center bias
- **Value** V(s): e.g., simple heuristic (connectivity), or 0 as baseline, or random with small variance

This is enough to demonstrate PUCT integration and run comparisons.

### Evaluation note
PUCT can outperform UCT at low budgets if priors are informative.

---

## 5) Recommended extras (if you want “all course algorithms”)
### Zobrist hashing + transposition table
- Maintain a fast XOR hash for state
- Store/reuse node stats across transpositions (same position reached different ways)

### Root bandits: Sequential Halving / SHOT
- Improve root decision at small budgets by eliminating weak moves early

### MCTS Solver
- Mark proven wins/losses and propagate exact results in the tree
