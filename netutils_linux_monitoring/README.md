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

## Why optparse (and not argparse/click)

Because optparse is the only parser able to define Option() as separate object.

It's possible to do via patching argparse but it's ulgier than using deprecated module, I think.

## How it even works?

BaseTop provides list of basic options such as an `--interval`. They may be applied for each inhereting class.

Four other "Tops" may define options specific for them.

And finally network-top, based on BaseTop too, takes all these four Tops, adding their options to its parser. If they are conflicting, new option just ignored (they are conflicting because all these utils based on same BaseTop).
