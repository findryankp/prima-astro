from dataclasses import dataclass
from typing import Optional


@dataclass
class Sparepart:
    item_number: str
    product_name: str
    soh: float
    safety_stock: float
    unit: str
    status: str


@dataclass
class Transaction:
    item_number: str
    product_name: str
    department: Optional[str]
    pic: Optional[str]
    tanggal: str
    qty_out: float
