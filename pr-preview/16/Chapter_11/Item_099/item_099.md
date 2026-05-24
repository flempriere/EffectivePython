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

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b'?\xfa\xd0\x9f\xe8\x93I\x88&Dr\xf2k\xed\x92\x14t53\x95\xd6e+XN\xac\xd34\\\xc2\x8b\x9b\xb2)\xe9yUSj\xac\x99\xe2\x04\xc4\x91\xb9\x97\xdc\x91\xd7y_\x98\xb7\xa0\xd3\x88#y\xe4\x931\xd0\xec'

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

    Sent chunk=b'\x8e\xf3\xf2\xe0\xadr8\x1b\xe3\x8fQ\xaa\xd0\xd9\xe1\x94d\xcd\x88Su\x089\xc1he\xdf\x83\xb5\x1c\xb2\xf0C\x86\x1aE\xd1^\x99`\xa96\x8f \x9e\xd4\xee\xe9U\xfa\x95Xi\x1e|0\x01\xb8[/\xcd[\xb7:' over socket

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

    0.000980318 seconds

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

    <memory at 0x7f6e88f07880>
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

    Updated the cache: new_cache=b"\xe9\x80\x01\xf2\x95\x00K\x14\x8b]\xb4\x16\\\x8bh\x8bQ\x1f7\x1e\x03\x19\x04Z\xc6pC\xb7\xf8>\xaa4\xcc\xb2q\x82\x03\xd6\xb4\x07\x8c\x1f\x87\xa8\x18\xa3Y\x93HhO\x99b\xa2\xcdk\x80?O\x91v\xcaqw\x1d\x91\xd2y\xa8Q+>\xf1@\xe5\x01X\x91Zu\x966(/YO+b\xdc\xd6pO]\xa8\x1b\x82%\xe2\xcapgC\xe3\xc8U\x88\x1a\x9b\xc7\x86\x9d\x08\n\xc8|\x8fV\xd0\xb9$!'\x1c\xfe\xd0Ec\x19\\\x1aO\xe3\x16n\xf0\xe4\xda(\x8f\x06+\xc9X\xe7m#\x18\xad\xc0\xed\xd5\x02D\xb7\x05\x7f\xbe\xcaw\xc4\xb1\xd9`\xb2yj\x9b\xb6\x047\xa2\xe2\xfca\xac\xad'\x99\xfc\x1eU\xec\xa1\x83\x94,^KK'\x1c\xd2\xb6\xf2+\xcer\xdd\x93\x02P\x8e\xb9\xc8\x87\x8a;nD\x1cXu\xcd\x19\xa3W\xe7P\x1f\x07\xe4)8\x94\x8c\x8b\xd7Xki~\x82\x13+E\xba\x9c0\xb9\xc4\xbaw\x03D\xa7\x00\xac\x0bu\xac?\x85r\xbc\t\xfd\xd8\x82~p\x8fv`\xd2\x13@'\xb0\xf9;h\\-\x8c\xdb\xff\xe4k\n%L\xf2q\xdc\xe1$wb\xfa{\x96\xaf\x19\xc2\xea\xee\xdbN\xadwF\xd4\xca\xb3%\xbb_R,,\xa9d[\x03L\xe9\xd4Nz\x96"

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

    0.000949182 seconds

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

    New cache: video_cache=b"\xd7\x8d\xf3\x86\xc9\xf61e\xe2=\xf0_\x9c\x0fbM\xcc\xfe \x84\x13\\;\xeehKF\x8d\xa6\xed:\n\x86\x8bx ;\x93\x9e\xd5\xd7F\x95?\xba\xb3\xb4\x0b'\xe1\x9a\xa0\x97\x1a\x9c\xff\xad\xf4P\xf6\xce\x8ftV\x00\xc1k\x06\x15\xf8\xe7*\xa6\nF\x80\xdf\x88\xd9s\xf8\x90f=\xbb\xa9\xfe.\xeb\xef\x81?\xb1c\xac\xeb\x8d\x93H\xbel\x97\xa5\xb3o\x8e/\x18t\xe7\xcc\xabs\xb0\xa6\xc4Rv\x83X\xf1\xd2\x06\xdb\xda\xffCSpV\xcc$(\x1b\xa4\rC?C\xe5\xabW\x089\xf9\x93\x04\xf5&\x8c\xf1j\xb5\xb4\xf5\xda\xc1\xc2\x8e \xd2\xf4F<\x01d\xf6\x16\xb9\xf8v\x7f\x11X\xc4\xf9F\xd9\t\x0f\x7f\xea\xd1\xee\x81\x13%\x01OfB\x02\xb8\x0e/*t\xacN\xc5\xab\xd1\x8b\x88\xb8&s]\x1an`\xcc\x0b\xbe\xa4C\xfd\xd5\x80\x8b\x82\xe1q\xdf\x12\x9d5\x10\xf4\xd6\xda\xc9\xda\xa1\xea\x86\x9b0\xc8[Mf\xb1C*\xc6\x8f\xf2\xbf~v[~\n\xe0\xb1L\x0f\xda\xcb*X\xcb\x8c\x97\xd8\xae\xb0 \x96J\x92\xa9+\x9a\xbcz6b\xe1C$n3[\x11\xc9\x12\x1e\xe1l^\x1b\x9f\xa1\xa4\x9d\x9fw\x8akx#\x01}P3\xd5c\x13Rw\xc8\xdc\x1a\xf4\xc6\x9e\xc0c"

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

    0.000038993 seconds

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
