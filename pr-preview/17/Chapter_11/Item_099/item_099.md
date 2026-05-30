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

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b"\x0f\x8f\x17\x93A\x0e4\x8a\x1c\x11\xf8T\x83-\xf2\xb6S\x18x\x9bY\xae\xcd\xcag\xb7\x08e\x91\x16O\xab\xf2\x9e\x98\xd1&\xaa\xb7m\xcf\xbc.\xa3\xf5:\x082\x01\x8a1'\xa1\xedYd\xc8\xb9\x17\xf1\xfa\xa3C\xbf"

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

    Sent chunk=b"*\x19N\xbd\x06Sx\x05\xb4\xc1\\\x1b}8*1\x93<_\xab\xb0U\xf6X\x02\xe2\rJl\x049\xa5\x11\xdd5\xb2\xab\xd66e\xe8\x954\x16O@/\xc2\x19\xb9/E'\xda[J$\xcf\x82\xd1(\x1f\x1ez" over socket

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

    0.000944804 seconds

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

    <memory at 0x7f3b4419f880>
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

    0.000000200 seconds

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

    Updated the cache: new_cache=b'\x01\xbf-\xb7\xc3H\xd6{\xf3<\x7f*&.\xc4\x99\t{g56\xaf\xb3\xa0\xd7p6u\x8d\x94\xfcv\xf6\xd4\xf5x%N}\xa0\x95\xe9\x89S\x15\xc6\xb1~\x01\xed; \x9a\x18LX\x92\xbcB;\x1ej\xc1\xca2\x03\xe17Q\x11I\xe9,\xfcZ$\xe6\xc7\x9a\x9ehl\xa7\xf0\xa0\xa9\\\xf6S\xaf\x98\x0c\xe3\xaf\x07+\x8c\xb3\x95\x98g\x0f\xdeI\xe7\xf7\xb1\x00\xf0\xd6\xb5\xe1F\xc91\x83\\l\xc84\x084\xea\x90\xf1\xa8\x07\x8d\xaf\xb9a\xffl\xc8@\xb9b\xe8`\xde\xe3\x9c\xcb\x93\xe5r\x8c\x0b\x90N\x92\xb2\x05\xa4\xf7\xe3\x86\xed\xca\xc7&O\xdce\x8fiM\xbc&dw\xc9T\xfbp\xfa\xa5\xc2Y\xff@\xea\xe5`%\xdd_;\xe1}\x8a\xc5\xda6/\xd4\x12\xae7\xf0\x89\xa22\xa0AE\xf2\xcc\xf4Is\xc4/Dp\xf4\xfeO\x04\x94\x1f"WZ\xbd|\xe2\x07\xa7\xba\x82P\xbaHu\x96\xd4\xe0\xd3 xo\xcaz\x1a8\xfe\x15\xaf\x050\xa5ur\xb2\xda\xb5\xb4Y<\x03Wy\x11+\xce\xa5.\r\xf4\xda6\xd0\xd16E8f\xdf\xabVJ\x98|\xfe1nX\xcf\xbax\xb5:\x18\x89\xfb\xe0\xa2\xb7\x8e\xb7\xf0\xdd\xa8\xea\t\xc4\xe5\\*Lz8\x0c\x0f_\xba\xc57X'

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

    0.000931159 seconds

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

    New cache: video_cache=b'\xc1"\x08\xce\x1d\xe2EX^\xf6\xfc;\xdd)<\x9b\xect\x948\xfc7\xf3\xcc\xa4\xaf\xaf\xc4\xfe6z\x7f(\xfc\xc1\xf5\x07\xf7\xb67-pC\x0e<\xe6\xe9\x06\x16:\x0e\x9f\xac=\xe26.V\x9c\x0c\x14\xec\xa9\xcc\xf2\x0b9\r\xfa\x9a\xcd\xb8\x97\x1b\xbb\xd1\xf6,]\x96\xa0\xb6\x1c\xef\xb8\xfd\xdf\xf1\xf5\x1b40\xeeJ\x7f\xb8n\xf9\xd4^P\r\xd6\xfd\xbd=\x94\x83\x96\x18\xc7\xff1\xb16\xd7SP\xf1(s*%\xd4\x1br9\x0eq\xcc\x0f<\xf3\x9d\x90\xce\x94zZ\xa18\xdba2\x9c\xb3\x87j~\x08\xff\xb9\x1f\x8b\xc6\xc7\x19\xd9oU(\xba\x83r\x0b\xf3w9\xc3m\xb6\r\x12\xe5y\xd9\x85xz*j*h>\xa5\xb7\xfd\x88\x9fGQ\x14J\xe83G\xa5&v\xe6J\xeck\xde\xe3D\xe2\x94F\xf7G\xdf\xd6\x0fm*\x9c\xb5Z\x035n\x91\xc4\xdc\xaaH Z\x80\x8d\xe7\xa8\xfeD\xe3\xa0K1j\x96\x16\x86\xe8\xdc\xfc\x1e\xb8,\x84r.&\x14\r\xf3o\xb0LZ\xa8\xf3? \x8eL\xc6\x86\xa7\xec%\xdfG\xb7\x17n\x17\xa3\x9d\xd2\x07:\xcf\x16\x8dO\x01\x0b\x82\xe4\'\x92\xb1\x11\xc8Qb*b\xc9\xf5"*\xf9\x1bn\x17\x93A\xfe\xb7\xb8\xda\x05%\x15zbK%'

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

    0.000032830 seconds

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
