# 09 Click-bandit prototype of the SunCell game

Standalone, playable prototype of a redesigned allocation game (prompted by the 08 pilot, where people hedged near 50/50 and the blended per-round revenue mixed county quality with diminishing returns). Each of 10 weeks has 10 sales visits; each click sends one visit to Riverton (R-leaning) or Lakewood (D-leaning) and shows the panels sold right away. Bonus: real cents per panel sold. A belief question comes before any feedback.

Open `prototype.html` in a browser. URL parameters:

| Param | Meaning | Default |
|---|---|---|
| `v` | `a` = constant payouts (best play: every visit to the better county); `b` = visible diminishing returns within a week, fresh customers each week | `a` |
| `r`, `d` | Expected sales per visit, Riverton / Lakewood (first visit of the week in `b`) | a: 2.6 / 2.0; b: 4 / 2 |
| `decay` | `b` only: each extra visit to a county in a week sells this fraction of the previous one | 0.8 |
| `cents` | Bonus per panel sold, in cents | 0.5 |
| `weeks`, `visits` | Weeks, visits per week | 10, 10 |
| `seed` | Luck seed (reproduces a game) | random |
| `flip=1` | Lakewood is the better county | off |
| `dev=1` | Researcher panel: truth, best weekly plan, version switch | off |

Sales per visit are Poisson. The end screen offers the full visit log as JSON. Parameter values are placeholders until a simulation picks the gap and noise.

`screenshots/` holds static renders (`?shot=belief|game0|game|weekend|end` drives the game to that state with an automatic player).
