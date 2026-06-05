# Chapter 11: Performance

- Runtime is not the only metric of performance
- Some include,
  1.  CPU utilisation
  2.  Throughput
  3.  Latency
  4.  Response time
  5.  Memory usage
  6.  Cache hit rate
- Assessing performance does not also mean just taking one measurement
  such as the average
  - Generally one should also consider the underlying statistical
    distribution
  - E.g. With latency one might consider,
    1.  Mean latency
    2.  Median latency
    3.  99th percentile latency,
    4.  Worst-case latency
- *Good Performance* is subjective
  - Depends on the problem domain, environment and number of users
- *Performance Engineering* is the process of analysing program
  execution to identify and improve code performance
- Python code is often not regarded as especially performant
  - Not unfair given it’s runtime constraints
    - Interpreter overhead
    - Parallelism limitations (See [Item
      68](../Chapter_09/Item_068/item_068.qmd))
  - However it provides a range of tools that can be used to maximise
    what performance it does offer
