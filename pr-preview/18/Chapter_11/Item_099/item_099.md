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

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b'\x86\x02~\x87V\x9e\x94Gk\x98\xbe\xf0\xec\xa2\xc8\xf0VMJ+h\xa6E\xb2.\xb86\x8cz\xd2\xb7\xa6{uEFRC~b"\x19&\xb4\xe1T\x06VG\x90\x85q\xf2\xf4\xab\xa3\xe0\xd5\xbb\xca\x90\xb3\x1b\xfa'

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

    Sent chunk=b'm\xb9i\xderg1\xb3\x8e\xaf\xb7\xf6\xfc\x96\x94\xd0G\x8b\x13\xb0S\xf5\xe9\x9c=]\xb7)\xed\x1b\xba\xaa\xd8\x82\xb9RM}\xaf\x0b\xd2\x7f\xec\x11\x11\x9d\xbc\x1f\x81\xe3\xd7\xb9\x8er\xd2ws\xa7\xff\xb7\x96\xb1\xe8\xe4' over socket

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

    0.001126415 seconds

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

    <memory at 0x7fe4fc44b7c0>
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

    Updated the cache: new_cache=b"-W\xcaw\xf83\xa9!\x15\xba\xe1\xd8h\x15\xbb*\x1dN\xd5Y8A\xec\xd7F8\xb5F\xfd\xf1\xa3\xa7r^\x9c}\xad0\xbc\r\xca5Z:6\x9b\xb7.\xdd\xad\xb4q\xc5\x7f\x9b\xa0\xc0;\xf9>\x99\xa5\xdc\x13\xcfB+\x8c\xc6\x90@\xafM\xb9\xccwQ$\t\x1e\xcc\xc7!\x869\x91O\x88\xe4G\xdf\xdc\x94\x9b\xd6\x1dv\x15\xc2\xfb\xcb_=\xe1\xcb\x15\x1b\xa9\xf8\xfa\xcfJV\xc1h\xc6\x9c<\xd5\xf0l_\x84\xfe52Q\xc0\xd04\xd3\x14v]\xee?+Ku\x8e\x01w\xdc<\x1a\nEZv\xc1\xd7;\r\x85\xfeX\x83\xec\xc0F\xc4\xd9\xf5\xd5nQ\x92\x8a\xa4\x86\x1f'O\x0e#\x9df\xd8\x02B\xfa6\x94\xe7y\xd2\xe3~@nZ\x91\x82\x9d`\x03\xad\x9a\xe9>\xd5\x06.O\xa5\xdb\xd1i\xb3\xbeW`\nD6\x1b\xc2?\x10\x81\xf9BI\xf6\x10\xa9{\xeb\x9b\x14\xe9\xf58rsh\xe8{\xb1\xa05!hc-\xe7?\xebKNV8(g\x16\xd8.\xa8\x12L\xa39\x88\xa2\x9d\xc78\x0b!G\xf2XOP\x84\x1aD\xb7\x0b:\xb0\xe7\xb0\xd66\x95]4\x98\xf1]\xd9Jh\xe5\xa5\xf8!\xa3o\xf5\xeeX\xd0\xa7Bj\xfa8e\x1a\xaf\x19\xe1\xc0\xb7Nh7%"

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

    0.001078218 seconds

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

    New cache: video_cache=b'Q\x8f\x01\xae\xd8PL\xaa,\xf6\xfe\xc8V\x10\xf6\x8dLP@\xfci\xdc\xefl\xc8^\x9c\xdb\xec\xad{\xcc\xc7\xd7\xee\x1b\x94~\xa1\xc3J\xb0\x08\xf6\xf6Fj=\xc8&O\x7f|\xdaB\x06\xdf\x95#\xbd\x82.\xde\xa5\x84\xc9\xadR\xcc\xed\xe3\xa3C\x08\xa74<\xb6\'E\xa2"\n\xd9|F\x03\xe2\x1a\xdd\x92Ti\x17\x11-\x0fj\x98=\x05\x19b\'\xe3\xc8\xbc\xbe\x9f\xc6kp;-\x8e\xf8\xe4\xa1a\xf0\x93>\x0c}\x91R\xe5\x03\x92\xb22A\xc2\xa6_\xd3\x0e\xf5\x02\xe5g\x8b\xac]Jm\x11\xcb\x8d\xc7\x1c\xa2\xcc\x89\x98\x1e\xbd.\xbd\xf0\x0b\x12k\xadq\xb4\x87\x8f\xa4?6\xd9\xb9\xc58\xd7\xb9Od=f\xa4\xc0?\xe6j\xff\xae\x9b\xcc\xb4\xab\x02\xb0\x9f\xc5\x1a\xc1W\x80u\xf1][\xac\xb6&r\x89\xffA\x9eD\x0b\x04\x87,,\xc8\x82\t\x9dl\xf1/\xb7\x89k\xb92\x9d\xaei\xee\x8eio\xa9="\x1bo\xc0o"\xdd\xd3\xa6\xbepz\x8c\xd3d`\x18\xd51\xdf5\x1b\xe5\xd9\x11\xe8\xc7\xad\xb0\x9d\xedp4\xe9\xf9\xa8\x88\x9e\xb5\xe6\xd8dJ\xb1y\x05\xe9W4&~Z\r\xa1\xc9\x82\x1e\xbb\x1e\xcd\xb3\xfa\xd8\xe1\xd5\xa3\xc0\x94\xbd\xf3/p,\xe9\xd7\x9b4 Y\xd5\x7f'

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

    0.000032825 seconds

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
