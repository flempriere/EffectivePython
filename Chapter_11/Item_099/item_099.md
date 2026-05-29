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

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b'X\xf8\xc0]/\x06\x0f\x85+\xe8=5,d\x89\x95|O\xde*|[\x84n\x81\x1e0y\xf5\x10\xbdo4\xf4]\x15\x0f\xc5\xde\xfa\xb9\xde\x13\x019>M\xf6rJX9\x86\x0b\xdeY\xb6\x97\x1fT\xfc\x81\xb1\xa6'

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

    Sent chunk=b's\x80\xc8\xd3\x94\x93\xb7\x0cI\xc1FyV\x80\xad3Q\xda\x11\xbd\x99:\x80\xa6\x99\xa3\xfdJ%^t\x0bX\xf0\xebD\x17\x9aB\x10\xd10k,\x90\xede\xf5\x05y\xb6\xff\xb4`\x8fZ\x95\xe9\r-\xf9\x07\xa5\xa2' over socket

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

    0.001985729 seconds

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

    <memory at 0x7f836c8f77c0>
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

    0.000000183 seconds

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

    Updated the cache: new_cache=b'@_\x9fM\xe8NK\xde\x9b<*\xc0\xa39\x98\x15\xce\x1e\xdcH\x1e\x87\x17\xc0x\xdbw\xba\x7f\xa7x_\xdf\xa5\xab\'W+\xb7\xa5P\xfc\xa5\xdd4\xd7\n3\xc6\xd3\x12\xb6\x81\x1f\x87,\xf7\xf5\xb2\xbc\x90\xa5.r\xbdT\x84\xb1\x8a\xcfM\x00\xb8\\\xbf3\x9c\x94@\xf4n\xc7\x02\xc4\x86\xd3\xc6o`q-\xe3\xd1\x81\x87`}\x9eg%\x8dE$\xdc\t\xdc\xc6\xcc\xda\x04\x99Wl-X\x86\x17k\xb0\xfa\xce\xb1\xac0^<\x11\xd2"{\x82\r\xa9%P\xc13}\xed\xe8\xe2:\x02ew\xbe?\x83k\r\x90v\x0f\x1fR\xc4\x069\xd7\x11)\xbc~\xc5Y\x95\x13hjK\xbf\xd7\xc1\x07\xc1\x19X\x02=\x7f\x1c<sW\xd1\xc7DG\xef\xb0\xeb\x9al\xd7%\x04K\x8e<-\x1f\xf4)\x7f-\xd9o\x88~q\xcb\x8b\x0c\x03\xc8\xf2\xed\xa94\xb1x\x83@\xc52BW7\x07B\xa6\xbf\x07\x93K\xb1MI\xa5\x06,<\xe5\xc39\xe1l\xdd!\xfa#hP\xbb=\x95\xa4v\xa0\xe0J\x12\xe7\xce\x1a`]Sx-Q\xd2\xc8Z2j\xf6\xfd\xf8\x04/\xa0\x80\xb8\x1b \x89\xf3\xfa\xc8\x8c\x0b\xf7\x08\xe0I\x95\xaeE\xa1u\xd2\xa6X\xf4\xc1\x00\xad\xe4/%\xbe\xee7\x9cZ\xacZ\xc7\xb6'

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

    0.002201508 seconds

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

    New cache: video_cache=b"\x9e:8m\xc6r\xad\xb2\x90\x85\xf6\x08\xe9\xcb\x0e1;\x1e\x12e\xbc\x99\x15#V\x89\xb0\x15\xc3\xc4|\xe5\xc6?~\xbeR\x93?\xfe9\x88\x94\xc3\xcb\x86^I\x98|:\xb4\xbb6\xad\\\xc3\x0bXeR\xf9\xdb\x88'\xcei\xdc\xae\xb6'<\x8f\x02\x85?$V\x8c\x11\x13p\x0c\xb1%\x82\x84\xa6\xfd:X\xdd\xf8\xe9[\xaa\x9d\xadH\xbe\xd0z\xd8+\xe4\xfcu\xed\x1bvv.\x9ewE\xb5\xfd\x95P\x91)\xd8\x0e\xfb\x8c\x0fAtz\x06u\xed\x1f\x83\xbd4#\x92\x8ff\xeccSn\xb79\x82\x1a\x93]O\xb9\xe5\xa6\xd5\xd3\xe4\xdfrS\x84d/\xa4\x94\x9e\xbd\x93\xd6\xa3{\x18PU>G\xbcx\x01\xd1m\x87\xa1(\n\xb8y@VA\xd2\xed^ \xbd#\xf5\x9a\xb1b\xef\x17Z\xc9\xc3\x86\xe0\xf8q=\xfa\xdb\x1f9)f\xcd\xe1\xac|\xfb\x02\x90\x93`4\x84\x89\xc0\xbd\xe4\xc7\x1c\x00\x1b\xaa\xb7\xa5\x11+:\xe7\xfd\xcf\x9aFg\x86\x13\xc9\xf0\x82\x80\x8f\x1f\xeb\xda\xe3\x04\x0f\x03\xf4\x1a\xb2B\xb6\x8dHs\x88\xab\xcfa\xc8%\xfcK\xd2\xec\x8c\x06\xff\x8f\xe2W\xb0{\xb6\x0f\xe3\xfdD\x1a\x1e\x11\r/\x19W\xb0\xe7\xa1\x0b\x93e/\xb5\xfa\xe4)d\xc0y\x9c2\xae\xff(\xf6<"

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

    0.000073404 seconds

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
