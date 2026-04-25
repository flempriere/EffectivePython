# Chapter 8: Metaclasses and Attributes

- Metaclasses are a unique feature in python
  - Generally not very well understood
- Metaclasses let you intercept Python’s `class` statement
  - Provide special behaviour each time a class is defined
- Python also provides features for dynamic attribute access
  customisation
  - Give powerful tools for converting simple classes to complex
    implementations
- These features are *powerful* and hence dangerous
  - Dynamic attributes let you override objects
    - Can lead to side effects
  - Metaclasses can spawn bizarre behaviours
    - Hard for newcomers to understand
- Always follow the *rule of least surprise*
  - Only use these mechanisms to implement known idioms
