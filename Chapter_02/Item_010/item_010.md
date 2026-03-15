# Item 10: Know the difference between `bytes` and `str`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python has two types for raw character data sequences
  1.  `bytes`
      - Contains raw unsigned 8-bit values
      - Typically reported as ASCII encodings
  2.  `str`
      - Contains unicode *code points*
      - Represent textual characters from human languages

``` python
# A demonstration of bytes
a = b"h\x65llo"
print(type(a))
print(list(a))
print(a)
```

    <class 'bytes'>
    [104, 101, 108, 108, 111]
    b'hello'

``` python
a = "a\u0300 propos"
print(type(a))
print(list(a))
print(a)
```

    <class 'str'>
    ['a', '̀', ' ', 'p', 'r', 'o', 'p', 'o', 's']
    à propos

- A `str` instance does not have an associated binary encoding
  - Can convert to binary using the `encode` string method
- A `bytes` instance does not have an associated text encoding
  - Can convert to text using the `decode` bytes method
- You can specify the encoding / decoding you want
  - Typically by default it is UTF-8
- You should perform encoding / decoding at the furthest boundary of
  your interface
  - Referred to as the *unicode sandwich*
- Core of a program should use the `str` type
  - Which contains unicode data
  - Should not assume anything about the encoding
- Let’s you be flexible to other text encodings
  - e.g. Latin-1, Shift JIS, Big5
- Maintain strictness of your output encoding
  - UTF-8 (ideally)
- The split leads to two scenarios

1.  Operating on raw 8-bit sequences of UTF-8 encoded strings
2.  Operating on unicode strings of unspecified encoding

- Typically need helper functions
  - Let’s you convert, but enforce expectations
- First to enforce that we have a unicode string

``` python
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode("utf-8") #decode bytes using UTF-8
    else:
        value = bytes_or_str
    return value

print(repr(to_str(b"foo")))
print(repr(to_str("bar")))
```

    'foo'
    'bar'

- Second that we have a raw UTF-8 string

``` python
def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode("utf-8")
    else:
        value = bytes_or_str
    return value

print(repr(to_str(b"foo")))
print(repr(to_str("bar")))
```

    'foo'
    'bar'

- `bytes` and `str` seem to behave the same way
  - But they are not compatible
- Can concatenate `bytes` together, or `str` together
  - Cannot concatenate `bytes` to `str` or vice-versa

``` python
print(b"one" + b"two")
print("one" + "two")
print(b"one" + "two")
```

    b'onetwo'
    onetwo

    TypeError: can't concat str to bytes
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[5], line 3
          1 print(b"one" + b"two")
          2 print("one" + "two")
    ----> 3 print(b"one" + "two")

    TypeError: can't concat str to bytes

- Can compare `bytes` to `bytes` or `str` to `str`
  - But again, not across the types

``` python
assert b"red" > b"blue"
assert "red" > "blue"
assert "red" > b"blue"
```

    TypeError: '>' not supported between instances of 'str' and 'bytes'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[6], line 3
          1 assert b"red" > b"blue"
          2 assert "red" > "blue"
    ----> 3 assert "red" > b"blue"

    TypeError: '>' not supported between instances of 'str' and 'bytes'

- Comparing `bytes` to `str` for equality always evaluates to `False`

``` python
assert "foo" == "foo"
assert b"foo" == b"foo"
print(b"foo" == "foo")
```

    False

## Things to Remember
