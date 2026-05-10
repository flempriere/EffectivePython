# Item 96: Consider Extension Modules to Maximise Performance and
Ergonomics


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- An alternative to `ctypes` (See [Item 95](../Item_095/item_095.qmd))
  is to write a C Extension module
- Can directly use the Python API
- Let’s you use python features, e.g.
  - OOP
  - Protocols
  - Reference-counting
  - etc…
- Extension modules let the calling code be more Pythonic

## Things to Remember
