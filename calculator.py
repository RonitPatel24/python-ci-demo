"""Simple calculator module used to demo the Jenkins CI/CD pipeline."""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def is_even(n):
    return n % 2 == 0


if __name__ == "__main__":
    print("2 + 3 =", add(2, 3))
    print("10 / 4 =", divide(10, 4))
