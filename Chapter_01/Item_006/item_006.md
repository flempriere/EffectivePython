# Item 6: Always surround single-element tuples with Parentheses

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python has multiple forms for a tuple literal
  1. A comma-separated list denoted by parentheses

      ``` python
       first = (1, 2, 3)
      ```

      - This can optionally have a trailing comma

      ``` python
       second = (
           1,
           2,
           3,
       )
      ```

      - Makes multiple lines easier to read
      - Easier to edit, if we later append elements

  2. Comma-separated list without parentheses

      ``` python
       third = 1, 2, 3
      ```

      - Again can have an optional trailing comma

      ``` python
       fourth = 1,2,3,
      ```

``` python
first = (1,2,3)
second = (
    1,
    2,
    3,
)
third = 1,2,3
fourth = 1,2,3,

print(f"First: {first}\nSecond: {second}\nThird: {third}\nFourth: {fourth}")
```

    First: (1, 2, 3)
    Second: (1, 2, 3)
    Third: (1, 2, 3)
    Fourth: (1, 2, 3)

- All of these are treated as the same

``` python
assert first == second == third == fourth
```

- Have to be careful of special cases
- To create an empty tuple

``` python
empty = ()
```

- For single element tuples, we have to include the trailing comma
  - Otherwise it is interpreted as a single value enclosed in
    parentheses

``` python
single_with_comma = (1,)
single_without = (1)
assert single_without != single_with_comma
assert single_without == single_with_comma[0]
```

- In theory can use the second form with a trailing comma

``` python
single_value_with_comma = (1,)
assert single_value_with_comma == single_with_comma
```

- **However** the third form can cause issues
  - Following example shows an e-commerce site function call
  - There is an insidious bug

``` python
# placeholder functions
def calculate_refund(value, tax, discount):
    return 1


def get_order_value(user, order_id):
    pass


def get_tax(address, dest):
    pass


def adjust_discount(user):
    pass


from dataclasses import dataclass


@dataclass
class Order:
    id: int
    dest: str


@dataclass
class User:
    name: str
    address: str


user = User("Alice", "Bobsville")
order = Order(1, "Bobsville")

to_refund = (
    calculate_refund(
        get_order_value(user, order.id),
        get_tax(user.address, order.dest),
        adjust_discount(user) + 0.1,
    ),
)

print(type(to_refund))
```

    TypeError: unsupported operand type(s) for +: 'NoneType' and 'float'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[6], line 40
         33 user = User("Alice", "Bobsville")
         34 order = Order(1, "Bobsville")
         36 to_refund = (
         37     calculate_refund(
         38         get_order_value(user, order.id),
         39         get_tax(user.address, order.dest),
    ---> 40         adjust_discount(user) + 0.1,
         41     ),
         42 )
         44 print(type(to_refund))

    TypeError: unsupported operand type(s) for +: 'NoneType' and 'float'

- The trailing comma above has accidentally converted the `to_refund`
  variable to a tuple
- This commonly happens when editing tuples, or other sequence
  collections
- Other disadvantage of the second form
  - Can’t easy move assignment into expression, e.g.

``` python
value_a = 1, # No parentheses, right
list_b = [1, ] #No parentheses, wrong -> list of int, not list of tuple
list_c = [(1,)] # Parentheses, correct

print('A:', value_a)
print('B:', list_b)
print('C:', list_c)
```

    A: (1,)
    B: [1]
    C: [(1,)]

- Single element tuple on the left side of expression can also be used
  for unpacking

``` python
user = "Alice"


def get_coupon_codes(user):
    return [["DEAL20"]]


((a1,),) = get_coupon_codes(user)
(a2,) = get_coupon_codes(user)
((a3),) = get_coupon_codes(user)
(a4) = get_coupon_codes(user)
(a5,) = get_coupon_codes(user)
a6 = get_coupon_codes(user)

assert a1 not in (a2, a3, a4, a5, a6)
assert a2 == a3 == a5
assert a4 == a6
```

- If you don’t understand what has happened above, let’s look at the
  individual variables

``` python
print(f"a1: {a1}")
print(f"a2: {a2}")
print(f"a3: {a3}")
print(f"a4: {a4}")
print(f"a5: {a5}")
print(f"a6: {a6}")
```

    a1: DEAL20
    a2: ['DEAL20']
    a3: ['DEAL20']
    a4: [['DEAL20']]
    a5: ['DEAL20']
    a6: [['DEAL20']]

- Sometimes autoformatters and linters can flag a trailing comma or make
  it more visible
- Often not
  - Won’t be until a test breaks because something that should be a
    collection suddenly isn’t
  - Or something that shouldn’t be a collection suddenly is
- Solution is to always use trailing commas and surround in parentheses

## Things to Remember

- Tuple literals may have optional parentheses and optional trailing
  commas
- Single element tuples require a trailing comma
- An extraneous trailing comma can convert expressions into unexpected
  tuples
