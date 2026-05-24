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

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b'\x9c/\xad\\K\xd1\rI\xd5\xf8~\x8d\xed\x98\xd7\xe0\xa8L\xd73\xbf\xdaK\xa6vEs\xbe/o\xe4\x9d\x9b\xd9|9=\x93^\x08\x9c\xf4u\x96g\x9ei\xbf\x94\xe3\x08,\xa6\xd8z\x17|\xe3m\xad\x91<{\x12'

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

    Sent chunk=b'\x97\xc1\xce\xb2\xf9t\x9a`\xb0\x02\x14\x88q\xb6\xe5\x9d\xfb\xf3\x17\x0c\x13A}L7\x88\x8f\x1aR)0\x17\x18\x1a\xd3,\x02P\xfb~t\x9c\x99\x07\x0e5\xdc\\\xd0\x1d5^\x91$s\x9f<9\xc5\x8de\x98\x85\x06' over socket

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

    0.000923578 seconds

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

    <memory at 0x7fa27491f880>
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

    0.000000204 seconds

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

    Updated the cache: new_cache=b'\x15D2!\'\x8b\xeaX\x8e\xd9\xe4u^\xb6W\xb7?\xb9\xe3"\x14\x8bUa\xd0j\xbd\x0bfm\xb1|:\xfd\x90\xbe\x86b\xa9\xc1\xb3\xf2\xd0\xa3f\xfa\xe4\r\xe3\xb8\xbf<Ai9q\xb4\xc2\xd8\t]QC\x95\xf9\xd3\x92\xa6g\xb4\x9c\x12e\x93`T\x11t\xdd\x89*.\x1c\x01\x96\xb6i\xbb?[\xf0\x96\x8b\xfd\xb7\xf4\xc3\x89\xf1\x11z\xa4<G\x06\xd7\xb9\x04<>@\x8b\xdaf\xc0\xa9P\xbb\xbaS(\x97\x80\xcfV\x8c\x16\xe3\xe5 \xe0\xafCk\x8a\xf5\x01\xaf\x9aM\xd7\xc4\xef&\xed\x00\xd5\x8a\xaf\xd2a;:\xd8\x00\xfa\xe7<\xa5\xe6_N;\xba\xd5@.\xfb\xb255%J\xe6\x10\xd1\xd1`\xbb\xe2\x1c\xb54n\xbd!\x00\x83\x81\x86\x9d\x02|\xf3\x01,\x96\x11q\x1e\xd4\xc4\x9ePw\xc1J\xd8\xa5f\t\xb8F\x8dM\x16-\x93\x96\x9c\xd3\xa1\xb0\x19\xca]\'wp\xe9\xd4&>\x1b\xae`P\xfb\xb7\t\xff\x89\xd8\x84Da7K\xbb\x90\x18\xbe\x8e\x0e\x84R\xe2vv\xfe\xcd\xd7\xbc%\xaa\xf3L\xc3\xb5D\x9b\xce\xe8\x1b\x94\xf6\x8f\xd82\xbf\xe0\x90;Z$\xe1\xad~\x1cmZ&\xd8\x880\x938\xc7\xfav\xc5`\\\x91\xd6\xaeQ&\xa8\xc7\xaf\xb6\xcc\x84R&\x0fV\xbd\x11'

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

    0.000935640 seconds

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

    New cache: video_cache=b'\xf8\xb2ur\xd6@iY\xff\xb8$%\x81\x1b1:\x125\x95\xb5\xc7\x93\x18c\x02\xa0\xa4\xf1\xa3*=\x0b\xbe6\xe9\xc3\xb3\xaf\x1a\x03H,;s\xa4\x80\xfd\x8b{\xb6\x8b\xdd\x1e\x07Pn\xd7\x90\x15g\x89\xdc\xd5\xeaS\xb3\x0e\xdc\x994\xd0\xb0S\x9b&r)W\x89[2\x8c\x82=n\xb9\xafpK*\xf3\xb8\xf3\xee_7\xb6\x03\xcb\xa4\x07\x01\xd8\xc7_\xdb\xd9\xb7g\xdfQ\xcd\xbfU\xd2\x00\x9f\xf0\xca\xef\xb9/\xcd\xce\xa5\xd4\xdb\x08\x98\x97c\x1bX\x8evb*\xde\xfb,\xd2v\xbd\x1a\x0c7\x1b\x92O\xab\xeaI\xc6\x7f\x84\xc9\xa0?\xb9\xa6\x145\t\x96\x0e\xb2\x0fH\x8f\x03g\x00P\xf4\xe0\x10\xd7~\x88\x1eqqB\x1b\xf0/\xa6\t\xe7\xf0\x07\x0f2\x16z\xa5X\xcf\xc8\x13\xde\xc3\xd4i\x1dr\x97R\x0bG\x89\x8d\xa1"6@G\x07\xa1\xa6O\xb6\xed\xbb\xa01<\xc0\x930M\x97(\xf2\xd7\xba\x032QAI\xd6\x08\xdc\xa8>\xdb\xdaZ\xfc\xda\xe0b\xeb\xd5\x1b\x88\xe4Kk\x8d\x01\x1e\x81:1a\x0e\x04\xbb7\xfdXfc^\xec\xf1\xfe\xe6\x97\xa1\xcd\xdcy\xf2?\xae\x18\x83\x0b\nk\xa6\xbe\xfdw!\x08\x03\xcbjN\x1f\xfb\x7f\xe8\xc9\xa9p\x96\xc7n\xeaS\xeaFe#\xde'

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

    0.000039171 seconds

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
