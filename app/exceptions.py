class VirtualEconomyException(Exception):
    """Базовое исключение для сервиса"""
    pass

class UserNotFoundError(VirtualEconomyException):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")

class ProductNotFoundError(VirtualEconomyException):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} not found")

class InsufficientFundsError(VirtualEconomyException):
    def __init__(self, balance: int, required: int):
        self.balance = balance
        self.required = required
        super().__init__(f"Insufficient funds: {balance} available, {required} required")

class DuplicatePurchaseError(VirtualEconomyException):
    pass

class DuplicateOperationError(VirtualEconomyException):
    pass

class InventoryItemNotFoundError(VirtualEconomyException):
    pass