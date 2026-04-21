# Item 43: Consider Generators Instead of Returning Lists

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- A `list` is the natural choice for returning a sequence of items

``` python
def index_words(text):
    result = []
    if text:
        result.append(0)
    for index, letter in enumerate(text):
        if letter == " ":
            result.append(index + 1)
    return result


address = "Four score and seven years ago..."
result = index_words(address)
print(result[:10])
```

    [0, 5, 11, 15, 21, 27]

- How could we improve the above?

  1. The list approach has a bunch of boiler plate
      - Here we want a list of indices corresponding to the start of
        words
      - `index + 1` is de-emphasised
      - `result` list creation and return is separated
  2. Building a list requires all results to be loaded into the list
      before being returned
      - For large inputs this can consume a lot of memory

- Both of these problems can be resolved using *generators*

- Generators use the `yield` keyword to incrementally produce outputs

- Rewriting our program to use a generator is straightforward

``` python
def index_words_iter(text):
    if text:
        yield 0
    for index, letter in enumerate(text):
        if letter == " ":
            yield index + 1


address = "Four score and seven years ago..."
it = index_words_iter(address)
print(next(it))
print(next(it))
```

    0
    5

- A generator function does not return a result, but instead returns an
  *iterator*
- Each call to `next` on that iterator the generator advances to the
  next `yield`
  - The corresponding value is returned as the result of the `next` call
- The code is easier to read because the emphasis is on the *what* of
  the code
  - In this case returning the starting index of the next word
- Generators also have the advantage that since they return the results
  one at a time the memory consumption is bounded
  - Means they can easily be adapted to arbitrary length input
- For example, we can write an version of `index_words` that streams
  input from a file

``` python
import itertools


def index_file(handle):
    offset = 0
    for line in handle:
        if line:
            yield offset
        for letter in line:
            offset += 1
            if letter == " ":
                yield offset


with open("address.txt", "r") as f:
    it = index_file(f)
    results = itertools.islice(it, 0, 10)
    print(list(results))
```

    [0, 5, 11, 15, 21, 27]

- The above functions memory consumption is limited by the maximum size
  of any line in the file
  - Since only one line at a time is stored in the state of the function
- Generators do have their own catches
  - The main one being that they are stateful
  - The returned iterators also can’t be reused (See [Item
    21](../../Chapter_03/Item_021/item_021.qmd))

## Things to Remember

- Using generators can be cleaner than returning a list of accumulated
  results
- generators return an iterator that produces the set of values passed
  to `yield` expressions within the generator
- Generators don’t materialise all inputs and outputs at once meaning
  their memory consumption is typically bounded and less than the list
  approach
  - This allows them to be used for arbitrarily large inputs
