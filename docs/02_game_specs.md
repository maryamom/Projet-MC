# 02 — Game Specs

## Option A (recommended): Hex

### Rules (standard)
- Board: N×N rhombus grid (implement as N×N with hex-neighbor adjacency)
- Players: **Black** connects **top ↔ bottom**, **White** connects **left ↔ right**
- Turns: alternate placing a stone on an empty cell
- End: first player to connect their sides wins (Hex has no draws)

### State Representation
Use one of:
- `board[r][c] ∈ {EMPTY, BLACK, WHITE}`
- current player to move
- move history (optional, for undo)

### Neighbors (hex grid on N×N array)
Common neighbor offsets:
- (r-1, c), (r+1, c), (r, c-1), (r, c+1), (r-1, c+1), (r+1, c-1)

### Winner Detection
Run BFS/DFS on the player’s stones:
- Black: start from all BLACK in top row, target bottom row
- White: start from all WHITE in left col, target right col
Stop early when a connection is found.

### Playout Policy
Start simple:
- random legal moves until terminal
Better (optional):
- biased random: prefer moves near the “frontier” or center
- use RAVE/GRAVE improvements instead of heavy heuristics

---

## Option B: Atarigo (optional alternative)
Atarigo is a simplified Go variant: you win by capturing a stone (or first capture).  
If you pick Atarigo, you’ll need:
- liberty counting
- capture rules
- ko prevention (depending on variant)
This increases implementation complexity, but it’s still doable.

---

## Recommendation
Choose **Hex** unless your professor explicitly requires Atarigo.
