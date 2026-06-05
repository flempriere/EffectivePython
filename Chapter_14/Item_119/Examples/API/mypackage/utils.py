# utils.py
from .models import Projectile

__all__ = ["simulate_collision"]


def dot_product(a, b):
    result = 0
    for a_i, b_i in zip(a, b, strict=True):
        result += a_i * b_i
    return result


def simulate_collision(a, b):
    after_a = Projectile(mass=a.mass, velocity=-a.velocity)
    after_b = Projectile(mass=b.mass, velocity=-b.velocity)
    return after_a, after_b
