# Final Report Outline

## 1. Introduction
- Project goal: Compare MCTS variants (UCT, RAVE, GRAVE, optional PUCT) on Hex
- Motivation: Understanding how different MCTS improvements affect performance
- Overview of algorithms to be compared

## 2. Hex Game Rules and Representation

### 2.1 Rules
- Board: N×N rhombus grid
- Players: Black (top ↔ bottom) vs White (left ↔ right)
- Turn-based: alternate placing stones
- Win condition: first to connect their sides
- No draws on standard boards

### 2.2 State Representation
- Board: 2D array with `EMPTY`, `BLACK`, `WHITE`
- Current player to move
- Immutable state design for tree search safety

### 2.3 Winner Detection
- BFS/DFS algorithm
- Black: check connection from top row to bottom row
- White: check connection from left column to right column
- Early termination when connection found

### 2.4 Legal Moves and Move Application
- Legal moves: all empty cells
- Move application: create new immutable state
- Serialization for hashing (tuple representation)

## 3. Algorithm Descriptions

### 3.1 UCT (Upper Confidence bounds applied to Trees)
- **Overview**: Baseline MCTS algorithm
- **Selection**: UCB1 formula balancing exploitation and exploration
- **Expansion**: Add one child node per iteration
- **Simulation**: Random playout until terminal state
- **Backpropagation**: Update visit counts (N) and total reward (W) up the tree
- **Key parameters**: Exploration constant C (typically √2)

### 3.2 RAVE (Rapid Action Value Estimation)
- **Overview**: Extends UCT with AMAF (All Moves As First) statistics
- **AMAF statistics**: Track move quality regardless of when played in simulation
- **RAVE value**: Blended Q-value combining UCT and AMAF
  - Q_RAVE = (1 - β) × Q_UCT + β × Q_AMAF
- **Beta parameter**: Mixing weight (can be adaptive)
- **Benefits**: Better move evaluation in games where move order matters less

### 3.3 GRAVE (Graph Refinement for AMAF Value Estimation)
- **Overview**: Extends RAVE by using AMAF from ancestor nodes
- **Key idea**: Use AMAF statistics from sufficiently-visited ancestors (N ≥ T)
- **Threshold T**: Minimum visit count to use ancestor's AMAF
- **Benefits**: Shares information across tree more effectively than local AMAF
- **Trade-off**: More computation but better information sharing

### 3.4 PUCT (optional)
- **Overview**: Uses prior probabilities and value estimates
- **Policy network**: Provides move priors (can be heuristic-based)
- **Value network**: Provides state value estimates
- **PUCT formula**: Combines priors, values, and visit counts
- **Implementation**: Toy network with center bias + connectivity heuristic

## 4. Experimental Protocol

### 4.1 Setup
- Board size: 5×5 (or other sizes)
- Iteration budgets: 50, 100, 200, 500, 1000 (per move)
- Number of games: 50-100 per configuration
- Random seed: Fixed for reproducibility

### 4.2 Match Format
- Agent vs Agent matches
- Alternating colors (agent1 as Black, agent2 as White)
- Fixed iteration budget per move
- Time measurement per game

### 4.3 Metrics
- **Winrate**: Percentage of games won by each agent
- **Average time**: Mean time per game
- **Performance vs budget**: Winrate curve across iteration budgets

### 4.4 Comparisons
- UCT vs RAVE
- UCT vs GRAVE
- RAVE vs GRAVE
- (Optional) PUCT vs GRAVE

## 5. Results

### 5.1 Summary Tables
- Winrate tables for each comparison
- Performance across different iteration budgets
- Time statistics

### 5.2 Performance Curves
- Winrate vs iteration budget
- Time vs iteration budget
- (Optional) Winrate vs board size

### 5.3 Key Findings
- Which algorithm performs best at different budgets?
- How does performance scale with iterations?
- Is there a clear winner, or does it depend on budget?

## 6. Discussion

### 6.1 Algorithm Comparison
- Strengths and weaknesses of each approach
- When does RAVE help over UCT?
- When does GRAVE help over RAVE?
- Trade-offs between algorithms

### 6.2 Budget Effects
- How performance changes with iteration budget
- Diminishing returns analysis
- Practical recommendations for different budgets

### 6.3 Implementation Details
- Design choices and their impact
- Immutable states vs mutable states
- Tree reuse considerations

## 7. Limitations and Future Work

### 7.1 Limitations
- Small board size (5×5) may not reflect larger game behavior
- Limited number of games per configuration
- Random playout policy (could use better heuristics)
- No transposition table (optional extension)
- No parallelization

### 7.2 Future Work
- Larger board sizes (7×7, 9×9)
- Better playout policies
- Transposition table integration
- Parallel MCTS
- PUCT with learned networks
- MCTS Solver mode
- Sequential Halving / SHOT at root

## 8. Conclusion
- Summary of findings
- Main takeaways
- Practical implications
- Algorithm recommendations for different scenarios

## 9. References
- UCT paper (Kocsis & Szepesvári, 2006)
- RAVE paper (Gelly & Silver, 2011)
- GRAVE paper (Gelly & Silver, 2011)
- Hex game rules
- MCTS survey papers

## Appendices

### Appendix A: Code Structure
- Repository organization
- Key modules and their responsibilities
- Interface design between game and search

### Appendix B: Experimental Data
- Raw CSV results
- Detailed statistics
- Configuration files

### Appendix C: Additional Experiments
- (Optional) Zobrist hashing results
- (Optional) Transposition table impact
- (Optional) Sequential Halving results
