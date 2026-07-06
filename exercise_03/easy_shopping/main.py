from calculator import calculator
from shopping import shoppingCart

# Calculator tests
calc = calculator()
print(calc.addition(7,5))
print(calc.subtraction(34,21))
print(calc.multiplication(54,2))
print(calc.division(144,2))
print(calc.division(45,0))

# Shopping cart tests
cart = shoppingCart()

# Add items
cart.addToCart("apple", 3)
cart.addToCart("orange", 10)
cart.addToCart("pineapple", 1)

# Display cart and total quantity
print(cart.showCart())
print("Total quantity:", cart.getTotalQuantity())

# Remove item and display again
cart.removeFromCart("apple")
print(cart.showCart())
print("Total quantity:", cart.getTotalQuantity())
