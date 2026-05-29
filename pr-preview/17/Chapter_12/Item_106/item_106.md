# Item 106: Use `decimal` when Precision is Paramount


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python supports arbitrary-precision integer arithmetic
- All floating-point values are represented as IEEE 754 compliant
  double-precision floating point
- Provides a standard complex number
- *However* floating point numbers are not suitable for precise decimal
  calculations
- For example, consider calculating a phone charge
  - We have the time of the phone call - 3 minutes 42 seconds
  - Rate of the call - \$1.45 per minute

``` python
# Floating point phone charge

rate = 1.45
seconds = 3 * 60 + 42
cost = rate * seconds / 60
print(cost)
```

    5.364999999999999

- Should see a trailing sequence of nines
  - Floating point number’s are unable to accurately represent the true
    result $5.365$
- If we attempt to round up the number…

``` python
# Floating point phone charge with rounding

rate = 1.45
seconds = 3 * 60 + 42
cost = rate * seconds / 60
cost = round(cost, 2)  # round to two decimal places
print(cost)
```

    5.36

- The charge is now *lowered* to $5.36$
  - Because of error in the floating point
- In reality we generally do not care about having high precision
  decimal arithmetic
  - Since most values are reported to two decimal places
- So we want to prioritise accuracy of those two decimal places over the
  flexibility of being able to represent a wide range
- Could in theory do so with a *fixed point* integer representation
- But rather than roll our own, we can use the in-built `Decimal` class
  - Provided via the `decimal` module
  - By default provides 28 decimal places of fixed precision
    - Can go higher
  - Better control over rounding
- Redoing the previous example

``` python
from decimal import Decimal

rate = Decimal("1.45")
seconds = Decimal(3 * 60 + 42)
cost = rate * seconds / Decimal(60)
print(cost)
```

    5.365

- Now accurately reports the result to three decimal places
- Two methods to construct a `Decimal`
  1.  Pass a string containing a decimal (ensures no precision loss)
  2.  Pass a `float` or `int` value
      - May have some precision loss
- For example, compare as below

``` python
from decimal import Decimal

print(Decimal("1.45"))
print(Decimal(1.45))
```

    1.45
    1.4499999999999999555910790149937383830547332763671875

- Prefer `str` to be sure
- Now consider a short call service
  - Very low cost (rate of 5 cents per minute)

``` python
from decimal import Decimal

rate = Decimal("0.05")
seconds = Decimal("5")
small_cost = rate * seconds / Decimal(60)
print(small_cost)
# Rounding
print(round(small_cost, 2))
```

    0.004166666666666666666666666667
    0.00

- Rounding to the nearest cent, results in rounding to zero
  - Business logic would instead probably round to at least a cent (Or
    have some minimum charge)
- Decimal provides mechanisms for controlling rounding
  - Namely the `quantize` method
    - Takes a formatted decimal for how to round the output
    - Plus a rounding behaviour, here we specify round up

``` python
from decimal import Decimal, ROUND_UP

rate = Decimal("0.05")
seconds = Decimal("5")
small_cost = rate * seconds / Decimal(60)
print(small_cost)
# Rounding
rounded = small_cost.quantize(Decimal("0.01"), ROUND_UP)
print(f"Rounded {small_cost} to {rounded}")
```

    0.004166666666666666666666666667
    Rounded 0.004166666666666666666666666667 to 0.01

- `Decimal` still has precision limitations
  - Can’t accurately represent all rational numbers e.g. $\frac{1}{3}$
- For precisely representations of rationals use `Fraction` from the
  `fraction` built-in

## Things to Remember

- Python provides built-in numerical types for most use cases
  1.  `int`
  2.  `float`
  3.  `Imaginary`
  4.  `Decimal`
  5.  `Fraction`
- `Decimal` class provided by the `decimal` built-in module
  - Designed for high-precision and precise rounding of decimal values
  - e.g. Monetary values
- Pass `str` instances to `Decimal` constructor instead of `float`
  - Avoids the rounding and/or precision errors in the `float`
    representation
