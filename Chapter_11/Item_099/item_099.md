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

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b'>\xad=\n]\x05>\xb6\x07uMG=\x08\xa6k\x1f\xce\x94\x9a\xb7\x93\x0b\xbc\xc8\xc3F\xd0r\x912N\xd7\x80\xa3\xcb6*\xbb\x08j\x13\xf8\xad\x13\xb9(\x14\x88\x13z\xa7s\x1aV\xe0\xb2\xc6M\x96\xd9\xb2\xa4\x98'

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

    Sent chunk=b'\x04\x10i?$\xaegZ\xd5\xa2Z\xdf\xa9\xc1\x16\x1f\x1c\xec\xff\x1e\xe2:Z\x9cY\x0cN\xc2\xef\n7t\x8a\x1f\x83Z\xe5V|\xdcX\x0b\xfd#\x9c&\xf0<\xb3\xa3VO\xccNa\x00\x1b\xc4\x91\x9dB\xe9\xf1\xab' over socket

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

    0.000981897 seconds

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

    <memory at 0x7f4c7c39b880>
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

    0.000000206 seconds

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

    Updated the cache: new_cache=b'\xd2$:\xcd\x1d\xbc\x83\xaa\xb8\xcf\xe41\xcb\xa6\xf7\xe2\xa8\xd6\x14\xd08\xe4t\xa6\x8f\xc4%O\x94bx\x81Ct\xab\x07C\x90oK\x82\xfb\x8a0\x9aA\xd4\xf2\xf8\xf12\xa6N\'\x01\x8fa\xeb(\xb0\xc2\r]\x9e\x81E\xda\xd0\x1d\xe3x\x8a\x87\xc1\x1bT\xd0b\xe9\x94\xc0\x16!_|G\x11M\xb1&\xda\xb5\xbd\x83f&V\xab\xf6\xb9\xaf?\xa4\x8e\x1f\x18\x91R\xfc\xe1\t\xdf\x8c(!\x87\xf3\xfb\x80\xafE\x9e\xc71\x93\x9f\x10\xf9\xc1\xfd_\xcc\x90\xb1x%&\xc7yl\xcd\xdd\xe4\x91\x9a\x1d\x9e\xcb\xc1&BE\xda\x911Yk\xacK\xae\xf5\x03"\x1fXbv\xc6-^I\xd5\xde\xb8\x86\x109\x16\xae\xed;\xe6\x80H\xe4\xc0e\x8dde`\x9c\x92\xe9\xa4\xb0\xd1\xed\xf6\x83\xd3\xc5\xdcR\xb6\x17\xb8\xb1\xabO\xec-\xa9@\x85\xdd\xfb\xf0\x8cB\xc2\xb4\xa1\xbce;\xdb\xfa\x19\x8a\x0e\xd0\xcb\xdcW\x12\xb2\x96\x18tXVSQ`D\xf3\xfa\x81\xe4n\x85\x97\x15\x94\xa0_R\x08m:\xc5s7Oo\xa0K\xb6<7\t\xd3\x18]\xcf\x89,\x01\xf3\xbf\xeb$\x99\xad$;\xf6\xee\x1b\xc4\xc3NN\x16\xb6\xb7]\xb8a\x88T\xd1@\x0b\xbc^6\x12:\xcb\xaf]\xdd\x11\xb4\xb9\x91P\xb7'

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

    0.000891504 seconds

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

    New cache: video_cache=b'7\x1f(\x03\xc8\xca\xc2a\x82l\xf6\xae\x02\x0f\x97\xc5e"X\x95x[d\x88\xc3\xae0\x14cWg5\xfa\xd2\x8bQ@Y\xb8\xf6\xd0 \xdf\xda\xf0\xbfV\xe6P1\x99\x17\x1d\xeat\x85\xf2\xa8\x9e\xae\x17\x05P\xa0K\xbcA?\x08m\xf7F\x86C\tjc\xd9\xda\xb0:9\xc5\x0e1\x8cG\x00\xe5\xb1\x90\xef\xda\xa0dk\x0c}\x81\xdf\x84\x11@\x0c7\x1c1 l\xdb\x13P\xc9V:\x9c\x8c\x9d\xf4-\x9f7\xfc\x1f\x13\xae\xdb/\x8a\x82\x8b\r\xd4f\xdeV\xf7\xfbPRF>\xfd&\xad\x1d#Q4\xda\xb4[yq\x1df~\xe6\xe14\xd3\x8c\x8f\x15\xf2\x86mdO}\xa4\x01\xa6\x8d\x82\x16o[\xcad\x89%\xa0\xc5)\xa0cO\x04:%=<\x1at\x07\x87\xc7G\xc4\x11\xa0\x96\x97/\xbaF\x80\x96\xb3\xf6C\x9a\xbbh\xe1hW\xc3?\xc0\x97D\xac^c\xb7[\x05\x1e\xc3>\xb6?\x84\x19*\xc8\xcd{\xb9\x0f\x01\xd2I\xb0l\x9f\x1cP\xa0\x06\x8a\x01\xa3f\x06[\xd5\xd6U\xa9\xb8\xb1\xbe\n\xc9\x91,\x8f?t\xae\xe2a\x98\x94\xd5KT\x8c\x06*8W\xb8\x13\xdcS3\xa4\x1bI[-\xe0\x98\xfa\x01\xe9\x88\xc8\x867\'\xfeO+]\x1c\'(\x9a6S5B\xdb\x82\x94'

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

    0.000030254 seconds

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
