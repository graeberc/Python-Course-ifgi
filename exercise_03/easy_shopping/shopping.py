class shoppingCart:
    def __init__(self):
        # Initialize an empty shopping cart
        self.cart = {}

    def addToCart(self, item, quantity):
        # Add an item with a given quantity to the cart
        if quantity <= 0:
            return "Quantity must be positive"
        if item in self.cart:
            self.cart[item] += quantity
        else:
            self.cart[item] = quantity

    def removeFromCart(self, item):
        # Remove an item from the cart
        if item in self.cart:
            del self.cart[item]
        else:
            return "Item not found in cart"
        
    def getTotalQuantity(self):
        # Return total quantity of all items
        return sum(self.cart.values())
    
    def showCart(self):
        # Return the current cart contents
        return self.cart