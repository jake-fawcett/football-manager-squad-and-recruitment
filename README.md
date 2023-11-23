# Football Manager player role evaluation
Python code to evaluate Player attributes in Football Manager against roles based on role weightings. Work in progress. Inspired by squirrel_plays_FOF's video [FM24 player recruitment using python](https://www.youtube.com/watch?v=hnAuOakqR90)

This is split into two scripts; position_score_calculator.py which calculates score based on positions ([Inspired by Mark on fm-arena](https://fm-arena.com/thread/1949-fm22-positional-filters-what-are-the-best-attributes-for-each-position/)) and role_score_calculator.py which caculates scores based on roles (this is missing plenty of roles at the moment!).

## Usage

position_score_calculator.py:
```
python3 role_score_calculator.py --input-filepath "squad.html" --output-filepath "squad_output.html" --roles gk fb dm w iw
```

role_score_calculator.py:
```
python3 position_score_calculator.py --input-filepath "squad.html" --output-filepath "squad_output.html"
```
