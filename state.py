# state.py
# File này re-export State từ base_algorithm để giữ khả năng tương thích ngược
# với các module khác import trực tiếp từ state.py
from base_algorithm import State

__all__ = ["State"]
