class calculator:
    def addition(self,a,b):
        # Return the sum of two numbers
        return a + b

    def subtraction(self,a,b):
        # Return the difference of two numbers
        return a - b

    def multiplication(self,a,b):
        # Return the product of two numbers
        return a * b

    def division(self,a,b):
        # Return the division of two numbers, handle division by zero
        if b == 0:
            return ("Cannot divide by zero")
        return a / b
        