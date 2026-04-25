# Item 67: Use `subprocess` to Manage Child Processes


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python provides built-in libraries for managing child processes
- Python is works as a great glue library to other tools
  - e.g. command-line utilities
- If shell scripts get complicated to the point they need a higher-level
  language python can be a great choice for a rewrite
- Child processes can run in parallel
  - Let’s you use multiple cores
  - Python itself is CPU bound (See [Item 68](../Item_068/item_068.qmd))
    - Easy to use python as the driver for CPU-intensive workloads
- There are several different built-in’s that operate at differing
  layers of abstraction
  - e.g. `os` provides `os.popen` and `os.exec`
  - Best choice is the `subprocess` library
- `subprocess` provides a simple interface for running child processes
  - `run` is a simple convenience function to start a process, read the
    output and verify it terminated successfully

``` python
import subprocess

result = subprocess.run(["echo", "Hello from the child!"], capture_output=True, encoding="utf-8")
result.check_returncode() # No exception means it exited cleanly
print(result.stdout)
```

    Hello from the child!

> [!WARNING]
>
> The examples in this Item require the shell commands `echo`, `sleep`
> and `openssl`. On Windows this may not be the case. Refer to the code
> in the [original examples](../../effectivepython) to see how to run
> the programs on Windows

- Child processes run independently from the parent process
  - The parent is the Python interpreter
- An alternative interface for opening processes is `Popen`
  - Let’s you poll child processes status periodically while the global
    process does other work

``` python
import subprocess
import time

proc = subprocess.Popen(["sleep", "1"])
while proc.poll() is None:
    print("Working...")
    time.sleep(0.25) # represent some busy work
print("Exit status", proc.poll())
```

    Working...
    Working...
    Working...
    Working...
    Working...
    Exit status 0

- Decoupling the child process from the parent means we can run multiple
  child processes in parallel
  - We can do this `Popen`
  - We then wait for them all to finish I/O and terminate with
    `communicate()`

``` python
import subprocess
import time

start = time.perf_counter()
sleep_procs = []
for _ in range(10):
    proc = subprocess.Popen(["sleep", "1"])
    sleep_procs.append(proc)

for proc in sleep_procs:
    proc.communicate()

end = time.perf_counter()
delta = end - start
print(f"Finished in {delta:.3} seconds")
```

    Finished in 1.0 seconds

- If the above processes ran in sequence we would expect the total delay
  to be close to $10$ seconds
- You can pipe data into a subprocess and also retrieve the output
  - Let’s you set up many programs to do parallel work
- For example, we might want to use `openssl` to encrypt some data
  - We’ll just pipe random data for now
  - In reality this would be some form of fed input
    - user input, file handle, network socket, etc.
  - Then wait and retrieve the final output

``` python
import os
import subprocess
import time

def run_encrypt(data):
    env = os.environ.copy()
    env["encrypted_data"] = "zf7ShyBhZ0raQDdE/FiZpm/m/8f9X+M1"
    proc = subprocess.Popen(
        ["openssl", "enc", "-pbkdf2", "-pass", "env:encrypted_data"],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    proc.stdin.write(data)
    proc.stdin.flush() # Ensure that the child gets input
    return proc

procs = []
for _ in range(3):
    data = os.urandom(10)
    proc = run_encrypt(data)
    procs.append(proc)

for proc in procs:
    out, _ = proc.communicate()
    print(out[-10:])
```

    b'\x8c<\xd6\xdc=o\xd3|\x1e\n'
    b'l\xa7\xb2\x99e\x7f03\xdd\xbb'
    b'\xea\x10"Ld\x90\xa1\xb2\xcc='

- Can also chain parallel processes, a-la UNIX pipelines
  - Connect the output of one child process as the input of another
    child’s input
- For example, use `openssl` to generate a blake2b hash of the input
  stream

``` python
import os
import subprocess

def run_encrypt(data):
    env = os.environ.copy()
    env["encrypted_data"] = "zf7ShyBhZ0raQDdE/FiZpm/m/8f9X+M1"
    proc = subprocess.Popen(
        ["openssl", "enc", "-pbkdf2", "-pass", "env:encrypted_data"],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    proc.stdin.write(data)
    proc.stdin.flush() # Ensure that the child gets input
    return proc

def run_hash(input_stdin):
    return subprocess.Popen(
        ["openssl", "dgst", "-blake2b512", "-binary"],
        stdin=input_stdin,
        stdout=subprocess.PIPE,
    )

encrypt_procs = []
hash_procs = []

for _ in range(3):
    data = os.urandom(100)

    encrypt_proc = run_encrypt(data)
    encrypt_procs.append(encrypt_proc)

    hash_proc = run_hash(encrypt_proc.stdout)
    hash_procs.append(hash_proc)

    # Ensure that child consumes the input stream and the communicate()
    # method doesn't inadvertently steal input from the child. Also lets
    # SIGPIPE propagate to the upstream process if the downstream process
    # dies
    encrypt_proc.stdout.close()
    encrypt_proc.stdout = None

for proc in encrypt_procs:
    proc.communicate()
    assert proc.returncode == 0

for proc in hash_procs:
    out, _ = proc.communicate()
    print(out[-10:])
    assert proc.returncode == 0
```

    b't\x06`\x0f\xb4\x90\xecn\x82\xa6'
    b'm\x1d\xe6\xfaF\xce\x8c\x94PC'
    b'\xe7\xa3\xf8\xe5\xe3\xf9\x87_\x7f\xaa'

- `run_hash` defines spawns and returns one process to create the hash
  - It connects the spawned process to a provided input stream
- We can then reuse the `run_encrypt` process from before
  - Have to pass it’s output as the input to `run_hash`
- Then have to be careful with the encrypting processes output
  - Don’t want the python process to intercept any of the output
  - So we `close()` then disconnect it
- I/O between child processes is managed between them once set up
  - Then just need to poll until the processes finish
- If there are concerns that a process might hang or never finish we can
  use a `timeout` parameter to `communicate`
  - An exception is raised if the process doesn’t finish in time
  - Can then force a termination

``` python
import subprocess

proc = subprocess.Popen(["sleep", "1"])
try:
    proc.communicate(timeout=0.1)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()

print("Exit status", proc.poll())
```

    Exit status -15

## Things to Remember

- Use the `subprocess` module to run child processes and manage their
  input and output streams
- Child processes run in parallel with the interpreter
  - Let’s you maximise usage of CPU cores
- Use the `run` convenience functions for simple usage
- Use the `Popen` class for advanced usage
  - Including UNIX-style pipelines
- Use the `timeout`parameter of `communicate` to avoid deadlocks and
  hanging child processes
