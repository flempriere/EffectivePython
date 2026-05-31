# Item 99: Consider `memoryview` and `bytearray` for Zero-Copy

Interactions with `bytes`

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python requires extra effort to parallelise CPU-bound computation (See
  [Item 79](../../Chapter_09/Item_079/item_079.qmd) and [Item
  94](../Item_094/item_094.qmd))
- But, can support high-throughput parallel I/O (See [Item
  68](../../Chapter_09/Item_068/item_068.qmd) and [Item
  75](../../Chapter_09/Item_075/item_075.qmd))
- However, understanding the tools available and how to use them
  *without* leading to slow code can require some skill
- For example, consider a media-streaming server
  - Users don’t need to download a video in advance
  - Users can move forward or backward within a video
- We might have functions to implement this by converting a time-code to
  a index and returning the associated chunk of data

``` python
import os # for demo only

def timecode_to_index(video_id, timecode):
    # Returns byte offser in the video data
    return 0  # placeholder


def request_chunk(video_id, byte_offset, size):
    # Returns size bytes of video_id's data from the offset
    # simulate by returning random data
    return os.urandom(size)


video_id = 1
timecode = "01:09:14:28"
byte_offset = timecode_to_index(video_id, timecode)
size = (8**2)
video_data = request_chunk(video_id, byte_offset, size)

print(f"{video_id=}, {timecode=}, {byte_offset=}, {video_data=}")
```

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b']\xb9r\xe7g\xc4\xe8\xa0\x81\xb9\x18P\x80\xc7\x12\xbc\x8c\x83\xf1\xc5\xcdp\xa1\x97\x9a,\x05LU\xbfh\xea\xb1\x9e\x11G\xbc\xd8\x83\x14\xd4}\x0eq\x17f\x90\x99j\xe0\xad\xb9\xbe\xd4s\x87\xe5\x8a\x1d\xd7\x88-WO'

- How do we now implement the server-side handler that receives
  `request_chunk`
  - Must then return the associated video data chunk
- First we assume that the program is driven by an `asyncio` process
  (See [Item 76](../../Chapter_09/Item_076/item_076.qmd))
  - Now want to focus on how to handle extracting the chunk
  - Assume video is cached memory
  - Extracted then sent over a socket back to a client

``` python
import os # for demo only

def timecode_to_index(video_id, timecode):
    # Returns byte offser in the video data
    return 0  # placeholder


def request_chunk(video_id, byte_offset, size):
    # Returns size bytes of video_id's data from the offset
    return video_data[byte_offset : byte_offset + size]

# Adding in the handling

# simulate a socket connection
class NullSocket:
    def __init__(self):
        self.handle = open(os.devnull, "wb")

    def send(self, data):
        self.handle.write(data)

socket = NullSocket() # represents client socket connection
size = (8 ** 2) # Requested chunk size
video_data = os.urandom(20 * size) # Bytes containing data for video_id

video_id = 1
timecode = "01:09:14:28"

byte_offset = timecode_to_index(video_id, timecode)
chunk = request_chunk(video_id, byte_offset, size)
socket.send(chunk)

print(f"Sent {chunk=} over socket")
```

    Sent chunk=b'\xa5kc\x80\xa8\xa0\xa0\xff\n\xa02\xa6!\xd1~\xce7\xbe\x8a\x957)\xeb\xcf~.\x82\xb5\x08\x93q<k`.*>?\x90\x02\xb2\x15\x98\xd6\x1f\x12\x07\\\xcc\xcc,"\x99\x88e\xb4\x18\x8b\\/R\t\x80T' over socket

- Latency and throughput determined by two factors
  1. How long to slice the chunk from `video_data`
  2. How long to transmit over a socket
- Focusing just on point 1, we can microbenchmark how long fetching a
  chunk takes.
  - We’ll also exclude the function call wrapper
  - Here we’ll set the size to $20$ MB.

``` python
import timeit

size = 20 * (1024**2)
video_data = os.urandom(20 * size) # Bytes containing data for
byte_offset = 0

def run_test():
    chunk = video_data[byte_offset : byte_offset + size]

result = ( timeit.timeit(stmt="run_test()", globals=globals(), number=100) / 100 )

print(f"{result:0.9f} seconds")
```

    0.000928430 seconds

- This takes about $5$ milliseconds
- Theoretical server maximum throughput is thus, limited by video
  extraction speed as

$$
\begin{align}
    \frac{20 \text{ MB}}{5 \text{ ms}} &= 4 \text{ GB}\text{s}^{-1}
\end{align}
$$

- Server also limited to,

$$
\begin{align}
    \frac{1 \text{ CPU=second}}{5 \text{ ms}} &= 200 \text{ clients in parallel}
\end{align}
$$

- But we already know that `asyncio` should be able to scale up to tens
  of thousands of simultaneous connections
- The slowdown is because as discussed slices create copies
  - Copying consumes CPU time
- Instead we can use `memoryview`
  - A built-in type for handling the CPython `buffer` protocol
    - Low-level C API allowing Python runtime and C extensions (See
      [Item 96](../Item_096/item_096.qmd)) to access underlying data
      buffers
      - Can then treat them as `bytes` instances
    - Since Python 3.12 the buffer protocol is also emulatable in python
- `memoryview` can be sliced to create a new `memoryview` without a copy

``` python
data = b"shave and a haircut, two bits"
view = memoryview(data)
chunk = view[12:19]

print(chunk)
print("Size:            ", chunk.nbytes)
print("Data in view:    ", chunk.tobytes())
print("Underlying data: ", chunk.obj)
```

    <memory at 0x7fdcf87cf880>
    Size:             7
    Data in view:     b'haircut'
    Underlying data:  b'shave and a haircut, two bits'

- These *zero-copy* operations can significantly speed-up code that
  heavily processes memory, e.g.
  1. I/O-bound access
  2. Heavy numerical mathematics (e.g. Numpy)
- Using `memoryview` as a drop-in replacement for our video serving
  service

``` python
import timeit

size = 20 * (1024**2)
video_data = os.urandom(20 * size) # Bytes containing data for
video_view = memoryview(video_data)
byte_offset = 0

def run_test():
    chunk = video_view[byte_offset : byte_offset + size]

result = ( timeit.timeit(stmt="run_test()", globals=globals(), number=100) / 100 )

print(f"{result:0.9f} seconds")
```

    0.000000208 seconds

- This should run in a several hundred nanoseconds
- So an order of magnitude faster than the `bytes` slicing technique
- Our new theoretical maximum throughput is then

$$
\begin{align}
\frac{20 \text{ MB}}{250 \text{ ns}} &= 80 \text{ TB}\text{s}^{-1}
\end{align}
$$

- Or in terms of parallel clients

$$
\begin{align}
\frac{1 \text{ CPU-second}}{250 \text{ ns}} &= 4 \times 10^{9}
\end{align}
$$

- So four million clients. Now the program should be bound by the socket
  performance rather than CPU constraints.

- Now consider a reversed process

  - Users must submit live video streams that are then broadcast out to
    viewers

- We need to store incoming video data

  - Cache it for clients to read from

``` python
import os

def timecode_to_index(video_id, timecode):
    # Returns byte offser in the video data
    return 0  # placeholder

# socket connection from client


size = (4 ** 2) # Incoming chunk size
video_data = os.urandom(20 * size) # Bytes containing data for video
video_cache = video_data[:]

video_id = 1
timecode = "01:09:14:28"
byte_offset = timecode_to_index(video_id, timecode) # Incoming buffer position
video_view = memoryview(video_cache)


class MockIncomingSocket:

    def recv(self, size):
        return video_view[byte_offset : byte_offset + size]

    def recv_into(self, buffer):
        source_data = video_view[byte_offset : byte_offset + size]
        buffer[:] = source_data

socket = MockIncomingSocket()
chunk = socket.recv(size)
before = video_view[:byte_offset]
after = video_view[byte_offset + size:]

new_cache = b"".join([before, chunk, after])

print(f"Updated the cache: {new_cache=}")
```

    Updated the cache: new_cache=b'\x1e\x0f\xcc\x8b\x1e4L\x86s\xfd\x13#\xf8\x90\xe9|X\x81\xf2\x05\x19\xe0\xf4\xb2HU\xb3aR\x87f\x8b\xcd\x83\xdb\x8d\x18>\xd3hd\xd0\xf35\xa8\xa5\x01(\x97\x01\xc6|\\\x16v@kvx\xc1\x0c\xb9\x978\x0ex\x9ezeB\x94s7z\xbe7IH\r\x8f\xa2\x12\x82i\xae\x0f\xe1\x91\x91\xe1\xa5\xffT\x8dF\x86I\xdfmb\x1c\xbb\xb1\xb7c\xa8\x8fQ\xee*\xd9\xbdy\xc3C\xc9\x8c\x9d7\x14\x10\xe5\xd4\xfbPL^\xa9\x81\xf4\x01\xc9\xb00\x01v\xbf\x0b\xa4\x0c\'\xbf\x0e\xe96\xc6\xa9\\\xb5\xae\xa6\x8f\xb6J\xa1`?\x8f\x9f\xb7\x86\xad\x91\x92\t\x00$-\x0c\xc5%\xe3uy\xb9\x9d{\xfeH7T\xd3\xee\xd4\xf9\x085\xc8\xd8\xfd\xf1i\t\xa8\x13\xd39>\x0e\xdd\t\xa4\xac${6DT6o\x08\x1e\xe8\xf8\xba\xc2R\x00\x99\x97\xb3\x9a\x14\x14kE\xff\x02Of"\xc1\x00\xb7%>\x99\t\x11P\xb0A\xb3\xa4\x06Y\xff\x1c\xd5\xe4\xeb\xe4K\xfe+\x1b\xbc\x13\x91\xaa\x19Y\x88\xb6\xf6\'\x97\xa0"r\xaf\xf3\x7f\xe7\xac\xfe\xdfr\xfb\x0e>\x98gC5\xfb/N[\xb9\xbe\r\x8d\xf9W\x90g\x1cZ\xbe\xceI\xc6\t\x85u\xe9<@\x08\xaf\xad\xc1\xbf\x08\xa7E\xdb\xe9}'

- `socket.recv` returns a `bytes` instance
  - Splice this into the existing cache
  - Insert at the current `byte_offset` via slicing and `bytes.join`
- Now need to profile the timing

``` python
import timeit
import os

class MockIncomingSocket:

    def recv(self, size):
        return video_view[byte_offset : byte_offset + size]

    def recv_into(self, buffer):
        source_data = video_view[byte_offset : byte_offset + size]
        buffer[:] = source_data

socket = MockIncomingSocket()
size = (1024 ** 2) # Incoming chunk size
video_data = os.urandom(20 * size) # Bytes containing data for video
video_cache = video_data[:]
video_view = memoryview(video_cache)
byte_offset = 1234 # pick arbitrary point in the middle

def run_test():
    chunk = socket.recv(size)
    before = video_view[:byte_offset]
    after = video_view[byte_offset + size : ]
    new_cache = b"".join([before, chunk, after])

result = (timeit.timeit(stmt="run_test()", globals=globals(), number=100,) / 100)

print(f"{result:0.9f} seconds")
```

    0.000896341 seconds

- This takes about three milliseconds to receive $1$ MB and update the
  cache.
- Maximum throughput to receive is then

$$
\begin{align}
\frac{1 \text{ MB}}{ 3 \text{ ms}} &\approx 330 \text{ MB}\text{s}^{-1}
\end{align}
$$

- Means we are limited to about $300$ simultaneously streaming clients
- Can use `bytearray` instead of `memoryview`
  - `bytes` are immutable like strings

``` python
some_bytes = b"hello"
some_bytes[0] = 0x79
```

    TypeError: 'bytes' object does not support item assignment
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[8], line 2
          1 some_bytes = b"hello"
    ----> 2 some_bytes[0] = 0x79

    TypeError: 'bytes' object does not support item assignment

- `bytearray` is effectively a mutable version of `bytes`
  - Can overwrite indices
- `bytearray` values are integers rather than bytes

``` python
array = bytearray(b"hello")
array[0] = 0x79
print(array)
```

    bytearray(b'yello')

- Can still wrap a `bytearray` in a `memoryview` to avoid extra copies
  - Then can slice the `memoryview` and modify to overwrite the
    underlying `bytearray`

``` python
array = bytearray(b"row, row, row your boat")
view = memoryview(array)
write_view = view[3:13]
write_view[:] = b"-10 bytes-"
print(array)
```

    bytearray(b'row-10 bytes- your boat')

- Library methods in Python user the buffer protocol for fast data
  receipt or reading, e.g.
  1. `socket.recv_into`
  2. `RawIOBase.read_into`
- These methods avoid creating copies and allocating memory
  - Received data goes into existing buffer
- We can convert our program to use `recv_into` and a `memoryview` slice
  to speed up our broadcasting method

``` python
class MockIncomingSocket:

    def recv(self, size):
        return video_view[byte_offset : byte_offset + size]

    def recv_into(self, buffer):
        source_data = video_view[byte_offset : byte_offset + size]
        buffer[:] = source_data

# socket connection from client
socket = MockIncomingSocket()

size = (4 ** 2) # Incoming chunk size
byte_offset = 1234
video_data = os.urandom(20 * size) # Bytes containing data for video
video_cache = video_data[:]
video_view = memoryview(video_cache)

video_array = bytearray(video_cache)
write_view = memoryview(video_array)

chunk = write_view[byte_offset : byte_offset + size]
socket.recv_into(chunk)

print(f"New cache: {video_cache=}")
```

    New cache: video_cache=b"\xd0\r\x964\x1a\xa8\x02\xae{h\xcb\x18 \x9b0D\xd3D\xfb\xceJH\xb08\x81\x0b\x97\x12t\x07\xa4\t\xf3\xd8\xaes\xdc0}\xba\x92\xb2\x05\xf55\xd4\x97\xe1\\\xb0\x80Ho\x05\x89[\xca\xcc\xd0)\xc4\x8b\xea\x97S|r!\x13\xe7\x08\xc8Z\x9e-\x05\x196\x96\t\xda\t/\th\xbe\x05\xb1r\x8d\x1a\xe3\x82\x06\xea\x9c\xb0\x8fw\x86\xc4A\xea`\xe6\xec\xab\x95s\x7f\xae\xe0;\xc7V\x9c\xf4!\x04\x89\x17X\xfe\x84\xbc6B[\x8a\xf0\x81\xe7\xf7QE\x88M\x0f\x88\xb0A\xdc}\xab\x95\xe7&\x06\xf1\xbfYo\xe7\xa4Z'\x92\x8f\xc9X\x8bPI\x92\xcf\xe9Et\xba\xfe\xbd?T\xa8\xc8\xc7\x14\xce\x8a<O\xad\xce\xe9\x8b\xe2\x8f2WN\xa6k\xf7W\x8e@\x1dp$\xe8F\x82\xbfJm\xcd\x03\x82M\xe2\xd4$\xfc\xc0\xbe\xd1Ew4\x1a\xe6`3Jgm\xc4L\xdd>\xc9\xc7\x94\x14\xbaL\x93\x15Z\x00\x1cDlS\x1f\x15\x99\xa6\xb1\xd7smV\xddS-\xf9x\x9e\x84\xac\xa2\xe8\x7f\xa2\x11\xbdH\xb3'6\xbb~\x0f\x87>\xa1\xa5V*\xa9t\xfd|j\xe8#\x9b[\x9dc\x10\xca\xd7\rv\xba\x12\x838h\xe8\xec\x8e\x93\xb1\xbf|\x9d2yi\xc6\xb8Z\xfa.\x96z\x93"

- We can again microbenchmark the result for a $1$ MB chunk

``` python
import timeit
import os

class MockIncomingSocket:

    def recv(self, size):
        return video_view[byte_offset : byte_offset + size]

    def recv_into(self, buffer):
        source_data = video_view[byte_offset : byte_offset + size]
        buffer[:] = source_data

# socket connection from client
socket = MockIncomingSocket()

size = (1024 ** 2) # Incoming chunk size
byte_offset = 1234
video_data = os.urandom(20 * size) # Bytes containing data for video
video_cache = video_data[:]
video_view = memoryview(video_cache)

video_array = bytearray(video_cache)
write_view = memoryview(video_array)


def run_test():
    chunk = write_view[byte_offset : byte_offset + size]
    socket.recv_into(chunk)

result = (
    timeit.timeit(stmt="run_test()", globals=globals(), number=100) / 100
)

print(f"{result:0.9f} seconds")
```

    0.000036040 seconds

- On my machine this takes about $90 \;\mu\text{s}$. Which means we
  could support,

$$
\begin{align}
    \frac{1 \text{ MB}}{90 \; \mu\text{s}} &= 11 \text{ GB}\text{s}^{-1}
\end{align}
$$

- Which also supports,

$$
\begin{align}
    \frac{11 \text{ GB}}{1 \text{MB}} &= 11,000 \text{ processes}
\end{align}
$$

- Much better scalability

## Things to Remember

- `memoryview` provides zero-copy methods for reading and writing to
  slices of objects supporting the buffer protocol
- `bytearray` built-in provides a mutable `bytes`-like type
  - Can be used for zero-copy data reads
  - Works with functions like `socket.recv_into`
- `memoryview` can wrap a `bytearray`
  - Let’s received data to be spliced into an existing buffer
  - No need for extra copies
