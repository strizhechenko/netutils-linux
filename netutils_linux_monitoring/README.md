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

## Why argparse (and not click)

Because of tricky magic with inheritance and composition of args in utils. It's +/- easy to build parser with added arguments in functions, but I have no idea how to do the same thing in decorators' style that click provide.

## How it even works?

BaseTop provides list of basic options such as an `--interval`. They may be applied for each inhereting class.

Four other "Tops" may define options specific for them.

And finally network-top, based on BaseTop too, takes all these four Tops, adding their options to its parser. If they are conflicting, new option just ignored (they are conflicting because all these utils based on same BaseTop).
