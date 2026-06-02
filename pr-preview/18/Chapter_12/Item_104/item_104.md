# Item 104: Know how to use `heapq` for Priority Queues


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python’s traditional queue types (See [Item
  103](../Item_103/item_103.qmd) and [Item
  70](../../Chapter_09/Item_070/item_070.qmd)) are all First-in,
  First-out queues (FIFO)
- Typically instead might need to select items in order of *priority*
  - Priority might be distinct from the insertion order
- In these cases we instead use a *priority queue*
- E.g. Consider a library management system
  - Needs to send emails out to remind people to return overdue books
  - Books can be varied for different lengths of time
    - Means we can’t use a FIFO queue or a stack
  - Basic implementation would be to use a list
    - Maintain in sorted order by a `due_date` field

``` python
from dataclasses import dataclass


@dataclass
class Book:
    title: str
    due_date: str


def add_book(queue, book):
    queue.append(book)
    queue.sort(key=lambda x: x.due_date, reverse=True)


queue = []
add_book(queue, Book("Don Quixote", "2019-06-07"))
add_book(queue, Book("Frankenstein", "2019-06-05"))
add_book(queue, Book("Les Miserables", "2019-06-08"))
add_book(queue, Book("War and Peace", "2019-06-03"))

print(queue)
```

    [Book(title='Les Miserables', due_date='2019-06-08'), Book(title='Don Quixote', due_date='2019-06-07'), Book(title='Frankenstein', due_date='2019-06-05'), Book(title='War and Peace', due_date='2019-06-03')]

- Working with a sorted list means we have a simple check for overdue
  books
  - Simply check the *last* element of the list
- Can then call repeatedly until we have no more overdue books
  - Will perform the reminders in order from most overdue to least

``` python
from dataclasses import dataclass


@dataclass
class Book:
    title: str
    due_date: str


def add_book(queue, book):
    queue.append(book)
    queue.sort(key=lambda x: x.due_date, reverse=True)


queue = []
add_book(queue, Book("Don Quixote", "2019-06-07"))
add_book(queue, Book("Frankenstein", "2019-06-05"))
add_book(queue, Book("Les Miserables", "2019-06-08"))
add_book(queue, Book("War and Peace", "2019-06-03"))


class NoOverdueBooks(Exception):
    pass


def next_overdue_book(book, now):
    if queue:
        book = queue[-1]
        if book.due_date < now:
            queue.pop()
            return book
    raise NoOverdueBooks


now = "2019-06-10"

while True:
    try:
        found = next_overdue_book(queue, now)
    except NoOverdueBooks:
        break
    else:
        print(found.due_date, found.title)
```

    2019-06-03 War and Peace
    2019-06-05 Frankenstein
    2019-06-07 Don Quixote
    2019-06-08 Les Miserables

- Returned books can be removed from the queue
- When all overdue books are returned, we can use an exception to
  indicate their are no more (See [Item
  32](../../Chapter_05/Item_032/item_032.qmd))

``` python
from dataclasses import dataclass


@dataclass
class Book:
    title: str
    due_date: str


def add_book(queue, book):
    queue.append(book)
    queue.sort(key=lambda x: x.due_date, reverse=True)


queue = []
add_book(queue, Book("Don Quixote", "2019-06-07"))
add_book(queue, Book("Frankenstein", "2019-06-05"))
add_book(queue, Book("Les Miserables", "2019-06-08"))
add_book(queue, Book("War and Peace", "2019-06-03"))
book = Book("Treasure Island", "2019-06-04")
add_book(queue, book)


class NoOverdueBooks(Exception):
    pass


def next_overdue_book(book, now):
    if queue:
        book = queue[-1]
        if book.due_date < now:
            queue.pop()
            return book
    raise NoOverdueBooks


def return_book(queue, book):
    queue.remove(book)


print("Before Return:", [x.title for x in queue])
print("Returning", book.title)
return_book(queue, book)
print("After Return:", [x.title for x in queue])
```

    Before Return: ['Les Miserables', 'Don Quixote', 'Frankenstein', 'Treasure Island', 'War and Peace']
    Returning Treasure Island
    After Return: ['Les Miserables', 'Don Quixote', 'Frankenstein', 'War and Peace']

- Complexity of the current set-up is biased towards checks for overdue
  books
  - These are constant time since we’re removing the last element of a
    list
- Adding new books is expensive since we have to pay the cost of sorting
  the list every time
  - Adding $n$ books, means the total cost is about
    $n^{2}\log\left(n\right)$
  - We can benchmark this below

``` python
import random
import timeit


def list_overdue_benchmark(count):
    def prepare():
        to_add = list(range(count))
        random.shuffle(to_add)
        return [], to_add

    def run(queue, to_add):
        for i in to_add:
            queue.append(i)
            queue.sort(reverse=True)

        while queue:
            queue.pop()

    return timeit.timeit(
        setup="queue, to_add = prepare()",
        stmt="run(queue, to_add)",
        globals=locals(),
        number=1,
    )


for i in range(1, 6):
    count = i * 1_000
    delay = list_overdue_benchmark(count)
    print(f"Count {count:>5,} takes: {delay * 1e3:6.2f}ms")
```

    Count 1,000 takes:   2.53ms
    Count 2,000 takes:   7.87ms
    Count 3,000 takes:  16.79ms
    Count 4,000 takes:  28.29ms
    Count 5,000 takes:  42.67ms

- Removing items takes linear time to scan through the list
  - Can again benchmark this

``` python
import random
import timeit


def list_return_benchmark(count):
    def prepare():
        queue = list(range(count))
        random.shuffle(queue)

        to_return = list(range(count))
        random.shuffle(to_return)

        return queue, to_return

    def run(queue, to_return):
        for i in to_return:
            queue.remove(i)

    return timeit.timeit(
        setup="queue, to_return = prepare()",
        stmt="run(queue, to_return)",
        globals=locals(),
        number=1,
    )


for i in range(1, 6):
    count = i * 1_000
    delay = list_return_benchmark(count)
    print(f"Count {count:>5,} takes: {delay * 1e3:6.2f}ms")
```

    Count 1,000 takes:   3.13ms
    Count 2,000 takes:  10.11ms
    Count 3,000 takes:  22.90ms
    Count 4,000 takes:  40.91ms
    Count 5,000 takes:  64.15ms

- We can use the `heapq` module to implement a priority queue with more
  consistent time-complexity across the operations
  - Uses a *heap* data structure
  - Adding a new item or removing the smallest has logarithmic
    complexity
    - Here we want our *smallest* item to be the book with the earliest
      due date
- If we try and use `heapq` as a drop in replacement we’ll see errors
  - Elements of a `heapq` need to be comparable with a natural sort
    order (See [Item 100](../Item_100/item_100.qmd))
    - Can be done via the `functools` `total_ordering` class decorator
      (See [Item 66](../../Chapter_08/Item_066/item_066.qmd))
    - Or by defining the `__lt__` special method (See [Item
      57](../../Chapter_07/Item_057/item_057.qmd))

``` python
from dataclasses import dataclass
from heapq import heappush


@dataclass
class Book:
    title: str
    due_date: str


def add_book(queue, book):
    heappush(queue, book)


queue = []
add_book(queue, Book("Little Women", "2019-06-05"))
add_book(queue, Book("The Time Machine", "2019-05-30"))
```

    TypeError: '<' not supported between instances of 'Book' and 'Book'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[6], line 17
         15 queue = []
         16 add_book(queue, Book("Little Women", "2019-06-05"))
    ---> 17 add_book(queue, Book("The Time Machine", "2019-05-30"))

    Cell In[6], line 12, in add_book(queue, book)
         11 def add_book(queue, book):
    ---> 12     heappush(queue, book)

    TypeError: '<' not supported between instances of 'Book' and 'Book'

- Defining the `__lt__` method, to enable comparison,

``` python
from dataclasses import dataclass
from heapq import heappush


@dataclass
class Book:
    title: str
    due_date: str

    def __lt__(self, other):
        return self.due_date < other.due_date


def add_book(queue, book):
    heappush(queue, book)


queue = []
add_book(queue, Book("Little Women", "2019-06-05"))
add_book(queue, Book("The Time Machine", "2019-05-30"))
add_book(queue, Book("Crime and Punishment", "2019-06-06"))
add_book(queue, Book("Wuthering Heights", "2019-06-12"))

print("Books:", [x.title for x in queue])
```

    Books: ['The Time Machine', 'Little Women', 'Crime and Punishment', 'Wuthering Heights']

- Alternatively to create a heap we can,
  - Define the list in any order then call `sort`
  - Use the `heapify` function from `heapq`
    - Creates a heap in linear time (as opposed to $n$,
      $\log\left(n\right)$ operations if built-up one by one via
      `heappush`)
      - This is because we enforce the heap condition at the end rather
        than at every step
      - Also don’t have to do a full sort so no $n\log\left(n\right)$
        sort
- Method 1,

``` python
from dataclasses import dataclass


@dataclass
class Book:
    title: str
    due_date: str

    def __lt__(self, other):
        return self.due_date < other.due_date


queue = [
    Book("Little Women", "2019-06-05"),
    Book("The Time Machine", "2019-05-30"),
    Book("Crime and Punishment", "2019-06-06"),
    Book("Wuthering Heights", "2019-06-12"),
]
queue.sort()

print("Books:", [x.title for x in queue])
```

    Books: ['The Time Machine', 'Little Women', 'Crime and Punishment', 'Wuthering Heights']

- Method 2

``` python
from dataclasses import dataclass
from heapq import heapify


@dataclass
class Book:
    title: str
    due_date: str

    def __lt__(self, other):
        return self.due_date < other.due_date


def add_book(queue, book):
    heappush(queue, book)


queue = [
    Book("Little Women", "2019-06-05"),
    Book("The Time Machine", "2019-05-30"),
    Book("Crime and Punishment", "2019-06-06"),
    Book("Wuthering Heights", "2019-06-12"),
]
heapify(queue)

print("Books:", [x.title for x in queue])
```

    Books: ['The Time Machine', 'Little Women', 'Crime and Punishment', 'Wuthering Heights']

- Overdue books are now examined via checking the *first* item in a
  list, not the last
  - Still pop them off if overdue
  - Now using \`heappop

``` python
from dataclasses import dataclass
from heapq import heapify, heappush, heappop


@dataclass
class Book:
    title: str
    due_date: str

    def __lt__(self, other):
        return self.due_date < other.due_date


class NoOverdueBooks(Exception):
    pass


def next_overdue_book(queue, now):
    if queue:
        book = queue[0]
        if book.due_date < now:
            heappop(queue)  # remove overdue book
            return book

    raise NoOverdueBooks


queue = [
    Book("Little Women", "2019-06-05"),
    Book("The Time Machine", "2019-05-30"),
    Book("Crime and Punishment", "2019-06-06"),
    Book("Wuthering Heights", "2019-06-12"),
]
heapify(queue)

print("Books:", [x.title for x in queue])

now = "2019-06-10"

while True:
    try:
        found = next_overdue_book(queue, now)
    except NoOverdueBooks:
        break
    else:
        print(found.due_date, found.title)

print("Books:", [x.title for x in queue])
```

    Books: ['The Time Machine', 'Little Women', 'Crime and Punishment', 'Wuthering Heights']
    2019-05-30 The Time Machine
    2019-06-05 Little Women
    2019-06-06 Crime and Punishment
    Books: ['Wuthering Heights']

- Benchmarking the `heappq` implementation,

``` python
from heapq import heappush, heappop
import random
import timeit


def heap_overdue_benchmark(count):
    def prepare():
        to_add = list(range(count))
        random.shuffle(to_add)
        return [], to_add

    def run(queue, to_add):
        for i in to_add:
            heappush(queue, i)
        while queue:
            heappop(queue)

    return timeit.timeit(
        setup="queue, to_add = prepare()",
        stmt="run(queue, to_add)",
        globals=locals(),
        number=1,
    )

for i in range(1, 6):
    count = i * 10_000
    delay = heap_overdue_benchmark(count)
    print(f"Count {count:>5,} takes {delay*1e3:6.2f}ms")
```

    Count 10,000 takes   3.26ms
    Count 20,000 takes   7.00ms
    Count 30,000 takes  10.67ms
    Count 40,000 takes  14.95ms
    Count 50,000 takes  19.57ms

- Downside of a heap is that removing arbitrary items is not
  straightforward
  - We can bypass this by leaving all items on the heap
  - Add a new field that indicates if an item has been returned
    - Then when we pop an *overdue* book, only process it if it has yet
      to be returned

``` python
from dataclasses import dataclass
import functools
from heapq import heapify, heappush, heappop


@functools.total_ordering
@dataclass
class Book:
    title: str
    due_date: str
    returned: bool = False

    def __lt__(self, other):
        return self.due_date < other.due_date


class NoOverdueBooks(Exception):
    pass


def next_overdue_book(queue, now):
    while queue:
        book = queue[0]
        if book.returned:
            heappop(queue)
            continue
        if book.due_date < now:
            heappop(queue)
            return book
        break
    raise NoOverdueBooks


def return_book(queue, book):
    book.returned = True


book = Book("The Time Machine", "2019-05-30")
queue = [
    Book("Little Women", "2019-06-05"),
    book,
    Book("Crime and Punishment", "2019-06-06"),
    Book("Wuthering Heights", "2019-06-12"),
]
heapify(queue)

print("Books:", [x.title for x in queue])

# Returned books still show up in the priority queue
return_book(queue, book)
print(f"Returned: {book.title}\nBooks:", [x.title for x in queue])

now = "2019-06-10"

# Returned books no longer show up in reporting of overdue books
while True:
    try:
        found = next_overdue_book(queue, now)
    except NoOverdueBooks:
        break
    else:
        print(found.due_date, found.title)

print("Books:", [x.title for x in queue])
```

    Books: ['The Time Machine', 'Little Women', 'Crime and Punishment', 'Wuthering Heights']
    Returned: The Time Machine
    Books: ['The Time Machine', 'Little Women', 'Crime and Punishment', 'Wuthering Heights']
    2019-06-05 Little Women
    2019-06-06 Crime and Punishment
    Books: ['Wuthering Heights']

- Downside is the memory footprint
- A book might be in the queue multiple times (multiple returned
  instances and one currently out on loan)
- Queue operations fast, but at the cost of more memory
  - For robust system you should plan for worst case scenario
  - e.g. All library books being on loan at once
  - Accurately then map the footprint required
- `heapq` provides more functionality for different use cases
  - [Read the docs](https://docs.python.org/3/library/heapq.html)
- When needing to handle more advanced use cases like thread-safety (See
  [Item 70](../../Chapter_09/Item_070/item_070.qmd)) consider other
  implementations
  - e.g. `queue.PriorityQueue`

## Things to Remember

- Priority queue provides a queue-like interface for handling items in
  order of importance rather than first-in first-out
- `list` can be used to implement a basic priority queue,
  - Provides constant time access to most important element
  - Superlinear addition of elements ($n\log\left(n\right)$)
  - Linear removal of arbitrary elements
- `heapq` provides methods for performing heap operations on a list
  - Enables scalable operations
    - Constant time access to most important element
    - Logarithmic time addition of new elements
    - Logarithmic time removal of highest priority element
    - Difficult to implement arbitrary removal operations
- To use `heapq` items must be sortable with a natural ordering
  - Can define special methods like `__lt__` for classes
