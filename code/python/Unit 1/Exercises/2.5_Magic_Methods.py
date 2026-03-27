"""
2.5 Magic Methods

Your task:

    Extend the magic methods program we wrote for rational numbers by adding:

        1) Magic method __mul__ to perform multiplication on rational numbers
        2) __truediv__ to perform division on rational numbers

        Remember -
            - To multiply rational numbers we just multiply the numerators and denominators of both
            - To divide rational numbers we 'flip' the second rational number and handle it like multiplication

    Show that your methods work by creating to instances from the class then:
        1) using the multiplication operator on the instances (*) to print the results
        2) Using the division operator (/) to print the results

    For example:
     If a = 3/4 and b = 3/2 then:
        1) a * b should output 9/8
        2) a / b should output 6/12
"""

class RationalNumber:
    def __init__(self, numerator, denominator=1):
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        return f'{self.numerator}/{self.denominator}'

    def __mul__(self, other):
        return RationalNumber(self.numerator * other.numerator, self.denominator * other.denominator)

    def __truediv__(self, other):
        return RationalNumber(self.numerator * other.denominator, self.denominator * other.numerator)

a = RationalNumber(3,4)
b = RationalNumber(3,2)

print(a * b)
print(a / b)

c = RationalNumber(1,2)
d = RationalNumber(7, 16)

print(c * d)
print(c / d)