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

    video_id=1, timecode='01:09:14:28', byte_offset=0, video_data=b'\xe4k\xb3\x85$\xd5\xd1_\xaa\xfe\x1cO\xfa\xfd\xdc\x17\xa8\xeb\xd0\xd8?\xcdi\xa6\x8b\xf3\xe2\r\xfdN\xb9,\xbe\x15\xbf\x1e\x8e7-h\xf1+\xd9\x0c\xe5\xf6\x1e\x9bP\xbf\xb5Qn\x87KG\x04\x99\x14\xbaB\x96\x1f\xfe'

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

    Sent chunk=b'\xa6b7\xefF@\x11\xc27_\x84\x87\x96}R\xec\x19\x15\xf1\xa3\xfe[}\x0e#u\xf7Y\xa0a\xd8\xc5Rxe\xd1\xbeZ\t\xbbxz\xe5/\x9e\x98-\x81\x17\n#J\xb1\x98\xf4PsJ<\xd4T\xb0\x14W' over socket

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

    0.001222762 seconds

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

    <memory at 0x7f11b0c937c0>
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

    Updated the cache: new_cache=b'\xf5\x9d\xb5\x01`i\x89\x1b\xfbv&\xdb0\x91\xe7\x93~\xabw\xdf\xd4\x9d\xd0x\xfau\xc8\x11\xc9\xe5lLqP\x81/t@\xb5\xa3J=\xbb\xe9Y\n4\xf2\x9a\x85\x08J\x10\xed\xdbt\xab\x03\x90\x93\xec\x92<I\xde8\x90ufP\x1e\xc1\xfc=6\x93\x10*\xc8\x8a(\x80\xbc\x969\x98\x8e\xb3m\xbc\xdc\x03\xf7\xbe\xe8de\rj\xf4j\xb0\tg\x19\xe5e\x92\xb2\xe2\xbf\x8a\xdd\x19\x90o\xed\xd2\x13p\x91\xb6\xd2\x9c\xe6#Q\x18\xb8=\xb0\x8c\xbc\n@c\xafk\xbez\xfd\xc3\x87l\x83;\x16L\xfd\xa1?\xf0_"Va.\xfe%?H\x9f\xcb\xe36\xfe\xf1\x9c\x14:Z.\xc2\x16\x85\xb9<\xc2\xbd\n\xc7H\xda*\xb73\x8d\xd7{\x13]y3\xcbfur\x1dst\x9a\x17B?OO_LsJ\xb0\x92\xf8\x14\xb6\xe0P;\xbb\xce\xea\x9b\xb0\x99B\xb8p\x00\xcavN\xa3\xcd\xa0\xb9\xcd\x80\xac~Ey\xeaDwu\xb9\x96Q\x81e\x1c\xa1\rK\xb9R\xcb-\xe4 \xa6\xfa\xef\xf7\xd2\xc0| \x1d\'\xf7Qx\x11\n\xdbqu\x15\xda ^\xe8\xabr\x8f\xcb\xb5B\xef\x17\xd7\x97\x8f\xa1gm\x96\xb7F\xd7)\x80\n\xa7\xc5\xf0\x0f\xfa\x8fa\x07\xf4A\xd1p\x957\xeb\x1b'

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

    0.001271963 seconds

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

    New cache: video_cache=b's\xf9\x83G \xeenl\xf7\xf1z\xfd\xd1Iq\x94\xa5\x96,\x02\xba\xbe\xde\xf0P\x18\x948\xd4\xbc\xd24\xda\xf9\xbfx9\x16p\x91\xd3\x9c\xc0^\x06yN\x86X\x8cw\xb4_\x8a\xf4;\xff\xed)\xa9\xe9wt\x8f\xdck\xb9\xe4aS B93\xfd\xf4\xabv{\x1a\x18*N\x84+\xa5t?<El\xfe\x15\xc2]\xcdI\x8d\x8e\x02\xc2\xa3\x16a\xf9@\x98X"i\xc3\xd9\xec\x8f\x12PZL\xf2\xba*\x19Ei\xafX\x0f\xc8-y\x00\xe8\xf4\x85+\x11\xef\x98\xff\xef/a{\xfa\\\x1f\x9f"H\xbc\xf9\xc9\x88{zq\xa75.5\x8e\x8c\x8b,\xd0\xebn\x94i\x8e\xf7X\xc4\n\x1b^\x1c\xf9\x10\x02as\xf5\xfb\xe0{\xb4iQo,~\\\x04\xb3\xaa\rk\xb8\xcc\x97\xcc\x95\xf3\x01g\x8fU\xe4\xcb\xda\x08b[O\xbb\x17\xbc\xaf+\xad\xd9c\x03\r\xad|W\xb7\xe3\x98\xd9fc[\xb0>\x17u\xf0\xcc\xca\xaex\xdf9\xd9\xfc\x9a\xc1J\xb9_u\x92.\xf5J\xb2&\x10\x17>\xe5`e\x9f\x99\xc7[\xad\x9b,]\x84\xdd\xb1\xb90\x97\xc9|\xb2\x1b\xd3\x0b-A\x10G\xd6\x13#;\x02\xf1[\x16K\x9f\xdf\x9d\x82\xecYJ\x8f\xb2\xedh\x87"K\x89I\xf6\xb4\x16zR'

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

    0.000044946 seconds

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
