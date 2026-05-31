# api_consumer.py

from mypackage import *  # noqa: F403

a = Projectile(1.5, 3)  # noqa: F405
b = Projectile(4, 1.7)  # noqa: F405
after_a, after_b = simulate_collision(a, b)  # noqa: F405

result = dot_product(after_a, after_b)  # noqa: F405  # ty:ignore[unresolved-reference]
print(result)
