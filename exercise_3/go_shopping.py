from easy_shopping import calculator, shoppingCart

calc = calculator()
print(calc.addition(10, 5))

cart = shoppingCart()
cart.addToCart("pizza", 3)
print(cart.showCart())