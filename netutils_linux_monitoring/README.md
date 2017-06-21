Here are resting libraries for top-like utils:

- NetworkTop
- Irqtop
- SoftnetStatTop
- LinkRateTop
- Softirqs

They all are inherited from BaseTop. NetworkTop also uses other top-like (with slightly modified representation).

There is also an idea of future refactoring in the air: rewrite all the libraries like MVC:

- view - `__repr__()`
- model - `parse()` or separate class for representing data
- controller - basetop, optparse, etc.
