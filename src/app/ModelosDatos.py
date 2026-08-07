import json


class BankAccount:
    def __init__(self, owner, balance=0):
        # -----------------------------
        # Validaciones de entrada
        # -----------------------------
        if not owner:
            raise ValueError("El propietario es obligatorio.")

        if balance < 0:
            raise ValueError("El saldo inicial no puede ser negativo.")

        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        """Deposita dinero en la cuenta."""

        if amount <= 0:
            raise ValueError("El depósito debe ser mayor que cero.")

        self.balance += amount

    def withdraw(self, amount):
        """Retira dinero de la cuenta."""

        if amount <= 0:
            raise ValueError("El retiro debe ser mayor que cero.")

        if amount > self.balance:
            raise ValueError("Saldo insuficiente.")

        self.balance -= amount

    # ----------------------------------------
    # Serializar el objeto a un diccionario
    # ----------------------------------------
    def to_dict(self):
        """Convierte el objeto en un diccionario."""

        return {
            "owner": self.owner,
            "balance": self.balance,
        }

    # ----------------------------------------
    # Crear un objeto desde un diccionario
    # ----------------------------------------
    @classmethod
    def from_dict(cls, data):
        """
        Valida la información recibida y crea
        una nueva cuenta bancaria.
        """

        if "owner" not in data:
            raise ValueError("Falta el campo 'owner'.")

        if "balance" not in data:
            raise ValueError("Falta el campo 'balance'.")

        return cls(
            owner=data["owner"],
            balance=data["balance"],
        )

    def __str__(self):
        return f"Titular: {self.owner}, Saldo: ${self.balance:.2f}"


# =====================================
# Crear la entidad
# =====================================
account = BankAccount("Eduardo", 1000)

print(account)

# =====================================
# Comportamientos
# =====================================
account.deposit(500)
account.withdraw(300)

print(account)

# =====================================
# Serializar a JSON
# =====================================
json_data = json.dumps(account.to_dict(), indent=4)

print("\nCuenta serializada:")
print(json_data)

# =====================================
# Deserializar desde JSON
# =====================================
received_json = """
{
    "owner": "Lalo",
    "balance": 2500
}
"""

data = json.loads(received_json)

new_account = BankAccount.from_dict(data)

print("\nCuenta creada desde JSON:")
print(new_account)
