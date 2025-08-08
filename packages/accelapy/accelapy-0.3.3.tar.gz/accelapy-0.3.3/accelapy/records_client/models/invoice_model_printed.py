from enum import Enum


class InvoiceModelPrinted(str, Enum):
    N = "N"
    Y = "Y"

    def __str__(self) -> str:
        return str(self.value)
