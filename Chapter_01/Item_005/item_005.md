# Item 5: Prefer Multiple-Assignment Unpacking over Indexing

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `tuple` is a builtin type for immutable, ordered sequences
- Can be empty, contain a single item, or multiple, e.g.

``` python
no_snack = ()
print(no_snack)
snack = ("chips",)
print(snack)
snack_calories = {"chips": 140, "popcorn": 80, "nuts": 190}

items = list(snack_calories.items())
print(items)
```

    ()
    ('chips',)
    [('chips', 140), ('popcorn', 80), ('nuts', 190)]

- Like lists, they support numerical indices and slices

``` python
item = ("Peanut butter", "Jelly")
first_item = item[0] # index access
first_half = item[:1] # slice access
print(first_item)
print(first_half)
```

    Peanut butter
    ('Peanut butter',)

- Tuples are *immutable*
  - Once created they cannot be modified

``` python
pair = ("Chocolate", "Peanut Butter")
pair[0] = "Honey"
```

    TypeError: 'tuple' object does not support item assignment
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[3], line 2
          1 pair = ("Chocolate", "Peanut Butter")
    ----> 2 pair[0] = "Honey"

    TypeError: 'tuple' object does not support item assignment

- Python supports an *unpacking* syntax
- Let’s us perform multiple assignments on one line
- For example, if we know a tuple is a pair, we can assign both values
  to variables

``` python
item = ("Peanut Butter", "Jelly")
first, second = item # unpacking
print(f"{first} and {second}")
```

    Peanut Butter and Jelly

- Unpacking tends to be less noisy than repeated explicit index accesses
- Uses pattern matching
  - We can extend this to more complex scenarios
  - Can also extend it to list, sequence assignments and nested
    iterables

``` python
favourite_snacks = {
    "salty": ("pretzels", 100),
    "sweet": ("cookies", 180),
    "veggie": ("carrots", 20),
}

((type1, (name1, cals1)), (type2, (name2, cals2)), (type3, (name3, cals3))) = (
    favourite_snacks.items()
)

print(f"Favourite {type1} is {name1} with {cals1} calories")
print(f"Favourite {type2} is {name2} with {cals2} calories")
print(f"Favourite {type3} is {name3} with {cals3} calories")
```

    Favourite salty is pretzels with 100 calories
    Favourite sweet is cookies with 180 calories
    Favourite veggie is carrots with 20 calories

- Can also be used to swap without a temporary variables
- Using the normal syntax

``` python
def bubble_sort(a):
    for _ in range(len(a)):
        for i in range(1, len(a)):
            if a[i] < a[i - 1]:
                temp = a[i]
                a[i] = a[i - 1]
                a[i - 1] = temp

names = ["pretzels", "carrots", "arugula", "bacon"]
bubble_sort(names)
print(names)
```

    ['arugula', 'bacon', 'carrots', 'pretzels']

- We can rewrite this with unpacking syntax

``` python
def bubble_sort(a):
    for _ in range(len(a)):
        for i in range(1, len(a)):
            if a[i] < a[i - 1]:
                a[i - 1], a[i] = a[i], a[i - 1] # swap

names = ["pretzels",  "carrots", "arugula", "bacon"]
bubble_sort(names)
print(names)
```

    ['arugula', 'bacon', 'carrots', 'pretzels']

- How does this work?
  - Right side is evaluated and stored in a temporary tuple
  - The left side is then assigned via unpacking of this temporary right
    side tuple
  - Temporary tuple then ceases to exist at the end of the process
- A common use case is in unpacking lists generated in `for` loop
  expressions, e.g.

``` python
snacks = [("bacon", 350), ("donut", 240), ("muffin", 190)]
for rank, (name, calories) in enumerate(snacks, 1):
    print(f"{rank}: {name} as {calories} calories")
```

    1: bacon as 350 calories
    2: donut as 240 calories
    3: muffin as 190 calories

- This is the classic example of *pythonic*

- Short, but clear to see what is happening

  - No indices, which clutter the code with noise

- Unpacking can also be used for

  1. Unpacking list construction
  2. Function arguments
  3. Keyword arguments
  4. Multiple return values
  5. Structural pattern matching
  6. etc.

- Unpacking does not work for assignment expressions

- Requires you to be careful with your data structure to ensure the
  pattern matching works

## Things to Remember

- Python provides unpacking syntax for assigning multiple values in one
  statement
- Unpacking uses generalised pattern matching
  - Can be applied to any iterable
  - including iterables of iterables
- Unpacking reduces code noise by removing indices, enhancing clarity
