# Item 59: Consider `@property` Instead of Refactoring Attributes


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `@property` allows us to define intelligent behaviour when performing
  simple accesses or assignments to an attribute (See [Item
  58](../../Chapter_08/Item_058/item_058.qmd))
- They provide an attribute-like interface to functions
  - Makes them naturally suited for converting simple attributes into
    methods
  - For example could refactor a number into a quick calculation
- Converting an attribute to a property via `@property` preserves the
  existing API call semantics
  - Do not need to replace accesses or sets with a method call
  - Property changes are therefore not in and of themselves breaking
    changes
- `@property` thus acts ass a stopgap for API improvement
  - We might have an api versioned as `X.Y`
    1.  First change an attribute to property giving version `X.(Y+1)`
    2.  Later more significant change leads to version `(X+1).Z`
- For example, consider a *leaky-bucket rate-limitinq quota system*
  using python objects
  - `Bucket` class represents remaining quota and time quota is
    available

``` python
from datetime datetime, timedelta

class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.quota = 0

    def __repr__(self):
        return f"Bucket(quota={self.quota})"
```

    SyntaxError: invalid syntax (5411431.py, line 1)
      Cell In[1], line 1
        from datetime datetime, timedelta
                      ^
    SyntaxError: invalid syntax

- Leaky-bucket algorithm works as follows
  1.  Each quota period is represented as a bucket
  2.  A bucket is *filled* with available quota, and exists for a period
      of time
  3.  When a bucket is filled quota does not carry over to the next
      period
      - Unconsumed quota is lost
- We can implement this with the `fill` function

``` python
from datetime datetime, timedelta

class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.quota = 0

    def __repr__(self):
        return f"Bucket(quota={self.quota})"

def fill(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta: # reset -> existing quota is lost
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount
```

    SyntaxError: invalid syntax (3534162668.py, line 1)
      Cell In[2], line 1
        from datetime datetime, timedelta
                      ^
    SyntaxError: invalid syntax

- Now we have to provide a way for a consumer to utilise quota
  - Must first ensure there is sufficient quota available
- We demonstrate this below
  1.  First we define a bucket
  2.  We then fill it with quota
  3.  We then attempt to deduct quota (99/100)
      - This succeeds and the bucket is partially emptied
  4.  We then attempt a second deduction (3/1)
      - This fails, and the bucket’s quota is not reduced

``` python
from datetime import datetime, timedelta


class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.quota = 0

    def __repr__(self):
        return f"Bucket(quota={self.quota})"


def fill(bucket, amount):
    now = datetime.now()
    if (
        now - bucket.reset_time
    ) > bucket.period_delta:  # reset -> existing quota is lost
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount


# Add abiity for consumer to use quota
def deduct(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        return False  # bucket has expired
    if bucket.quota - amount < 0:
        return False  # Not enough quota available
    bucket.quota -= amount
    return True  # Bucket has space, consume the quota


bucket = Bucket(60)
fill(bucket, 100)
print(bucket)

if deduct(bucket, 99):
    print("Had 99 quota")
else:
    print("Not enough quota for 99 quota")
print("After attempted consumption:", bucket)

if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")
print("After second attempted consumption:", bucket)
```

    Bucket(quota=100)
    Had 99 quota
    After attempted consumption: Bucket(quota=1)
    Not enough for 3 quota
    After second attempted consumption: Bucket(quota=1)

- This implementation has a downside that the starting quota of the
  bucket is not tracked
  - Quota deducts over a period until reaching zero or a reset
- `deduct` at some point will continue to return `False`
  - Useful to know if a bucket can’t be deducted because it was emptied
    or never filled
- We introduce two attributes
  1.  `max_quota`
      - The maximum quota issued over a period
  2.  `quota_consumed`
      - Quota consumed over the same period

``` python
from datetime import datetime, timedelta


class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.max_quota = 0
        self.quota_consumed = 0

    def __repr__(self):
        return (
            f"Bucket(max_quota={self.max_quota}, quota_consumed={self.quota_consumed})"
        )
```

- But this new attribute set-up doesn’t match our old interface which
  had a single `quota` attribute
- We can use a `@property` decorator to provide `quota` as an on the fly
  property
  - The getter is a simple calculation
  - But we also have to provide a setter that works in terms of
    `max_quota` and `quota_consumed`
- The dependent `fill` and `deduct` calls work out of the box

``` python
from datetime import datetime, timedelta


class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.max_quota = 0
        self.quota_consumed = 0

    def __repr__(self):
        return (
            f"Bucket(max_quota={self.max_quota}, quota_consumed={self.quota_consumed})"
        )

    @property
    def quota(self):
        return self.max_quota - self.quota_consumed

    @quota.setter
    def quota(self, amount):
        delta = self.max_quota - amount
        if amount == 0:
            # Quota being reset for a new period
            self.quota_consumed = 0
            self.max_quota = 0
        elif delta < 0:
            # Quota being filled during the period
            self.max_quota = amount + self.quota_consumed
        else:
            self.quota_consumed = delta


# code below here is unchanged from first implementation


def fill(bucket, amount):
    now = datetime.now()
    if (
        now - bucket.reset_time
    ) > bucket.period_delta:  # reset -> existing quota is lost
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount


# Add abiity for consumer to use quota
def deduct(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        return False  # bucket has expired
    if bucket.quota - amount < 0:
        return False  # Not enough quota available
    bucket.quota -= amount
    return True  # Bucket has space, consume the quota


bucket = Bucket(60)
fill(bucket, 100)
print(bucket)

if deduct(bucket, 99):
    print("Had 99 quota")
else:
    print("Not enough quota for 99 quota")
print("After attempted consumption:", bucket)

if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")
print("After second attempted consumption:", bucket)
```

    Bucket(max_quota=100, quota_consumed=0)
    Had 99 quota
    After attempted consumption: Bucket(max_quota=100, quota_consumed=99)
    Not enough for 3 quota
    After second attempted consumption: Bucket(max_quota=100, quota_consumed=99)

- Existing code consuming `Bucket.quota` doesn’t see any external change
  to the `Bucket` API
- New code can directly use `max_quota` and `quota_consumed`
- `@property` supports incremental progress on how you represent data
  - For example in the future `fill` and `deduct` might be implemented
    as methods
  - In many situations objects have poorly defined initial interfaces,
    or are simple containers (See [Item
    51](../../Chapter_07/Item_051/item_051.qmd))
    - Happens due to code growth over time
    - Scope increases
    - Multiple authors contribute without considering consistency
    - etc.
- Don’t overuse `@property`
  - Once a class begins to be littered with `@property` methods or you
    find yourself needing to extend them it’s a good sign that it’s
    worth considering a full refactor and potentially a change that
    breaks API

## Things to Remember

- Use `@property` to give existing instances new functionality while
  preserving the existing API
- Make incremental progress towards a better data model via `@property`
- Consider refactoring a class and breaking API once `@property` becomes
  overused
