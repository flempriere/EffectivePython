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

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b'\xdbf+\x88\x8b\xe5\x8b*\x10 \xeb\x82\x13l\xe9\xba\x18\x12\xfc\x0b\xcd\xdc$>\xb1T\x9b!g\x04\x1c($H\xa9\xde7\xb9\xee\xe2R\xae\xdb\xdb\x15\x97#\xae\x83\xb6\x0c\xebS\xf2\x01i\xe9lF\xf0\xdb\xcd\x87\x14'

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

    Sent chunk=b'**\xf1\x11\x90A>ZGxh\x81t\xa4\xbd\x7fYy\xc8\xe8l\xcd<\xec3S\xf5\x95\xc0LE\x811a\x8bN\x9f\xa6\xc9\xeak\x199\x81VU\x94\xd4\x06\xa0\t@\xc8 n\xa1\x1f\xa3\xfa\x0f\x1b\x1e\xf3\xb8' over socket

- Latency and throughput determined by two factors
  1.  How long to slice the chunk from `video_data`
  2.  How long to transmit over a socket
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

    0.000879648 seconds

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

    <memory at 0x7f0c2015f880>
    Size:             7
    Data in view:     b'haircut'
    Underlying data:  b'shave and a haircut, two bits'

- These *zero-copy* operations can significantly speed-up code that
  heavily processes memory, e.g.
  1.  I/O-bound access
  2.  Heavy numerical mathematics (e.g. Numpy)
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

    0.000000154 seconds

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

    Updated the cache: new_cache=b'r\xcf\x1a\xa7\xbb\xa5_)\xcd\xc1\xe6\xfe\xbe\xba\xc3\x89\xc0\x16[\x87\x0e}\x82+\x12+>C\xb7\xde\t$6\xea#<\x0c\xedb\xbd"\xe4\x04\x14-W\xa9\xfc\xc9?\x84\x1b\x03\x8e\x88\xaa\xe1l6YY\x81\xc7=>\x9b \x85\x1f\xde\x1c\xa7\xa2+\xba\x881\xadEJ\xd0\xe0\xd0\xb7\'\xbf{@\x14v\xe4\xcdw\xaf\xfa\xfe5\xc7\xe2p\tA\xa5\xb6\x82\x81\xf9\x15nN\x9b\x05\x8f\xfe\x10\xa42\x1e\xa0B/\xad\xc6\xack\rmG\xe0|k\x14\x8d\x10\xa5\x0e\xbb\xe7\xf6\x19o\x883xke=\x9c\xbf?\xa4\x00\xdc\x82\xed\xd1<x\xad\xa4\xb1\x02a\x88\x0b)\x8f\xd2\xd2\x1c\x1fs\x9fV?\xdf*\x18\xff{;\xb1\x19\xaf\x02\x05\x8f\xd0\x13\xca\x9bbBk\x17\x01Q\xfd\xf5\xafU\x13C\xc3\xa8\xc6\xf8j\x85\xc5\x05\x0bR\xb73\xf8\xbf|DI(\x11\x05\xc3\xb8\xe8\x0e`\xe2v\xdb\x9csH\xea\x02\x02\\\xa5\xa2%VA\x10pD\x8f\xe2\xbe-\x9b\xd6\xe0L\xe4\x88M\xd4\xe0\x93\xc4\x94v\xca$\x0c\xd3\xa9\x99t\xeb\x0f\xa90\xc3\xc7\xa4>\x87\x11\xd0e!b\xebi{\x1a\x85\x9c\xcd\xae\r\xe8\x1f*NB\x1b\xad\xfaxz\x88\x96\xe3\x18]K\xc2}f\xd8\xf5*\xd4z\xca\x93u'

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

    0.000875793 seconds

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
  1.  `socket.recv_into`
  2.  `RawIOBase.read_into`
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

    New cache: video_cache=b'P\xa4F\xe8c\xa4\x8d-\xc9\xdfSA\\d\xa8\xaeh\xd8\xa0\x92\x9e6S\xbdj\xfa\x80G\x07\x04\x93\x1e\xf5}\xa6c\xa3*\x17\xf2\x02SK\x91\x14\xb0\x1c\xbb\x0c\xb4:S\xe0{\xaf\x9e\x99\xc5`\xba\xd4\x034\x88\x8cj\xc1{u\x81m\xb2\x84\x06\xce\xb8\x91\xa4\x8f\xc4w\xdb\x0e\x9f\x081\xfc>\x9b_\x96\xb6\xa8\x045d\x9a\x81D\xab\x97t\x81\x97i\xefV\xcd\xb9\x16\x04H\xbd\x89\xf1[1F $\xb0\x07.B\xde\x0f&\xcf\x898\x9f\x9d?;F8\xe4g\xe2\x86:\xd5\x81\r\xb9g\x1cLp\x9fg\x88\xcc \xc1\xbb\xbev5W\xde6\x83\xf9=\xbby\rT\xa9<Ro\xd0\xfd\xb9_\xa9\xf8\x11p\xca\xbd^Co\x85\xaa%p\xc0u\xd3\xd6\xcem\x9b\xf0\x9e\xf7p3x@Bf]\xac\x84\x19\xbc\xe5\x7f\ne*\xb9_\x93\xa3\xc6%\x10\x8fn6(k\x0f\x18\xd3\xb8\x11\x19\xa7K\x00qG\xe7\xb7y\xbc\x9e!\x9b\x9d\xaeKIC\xbf\xec\xabq\x1d\xe4f\xfb\x19.dI#\x01\x1b\x08xnh\x96E\x08j\xbb6\xf5\xe1:]\xae"\xbf\xbd:\xdf\xb9\x9dm\xd3\x12\x013X\xc0\x83\xd6C 4`\x04\x1b]\xd2\xc7\xe5\x7f\xbe\xc2"0\xdb\x19\x87\xb4I\xe1[\xcf'

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

    0.000025759 seconds

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
