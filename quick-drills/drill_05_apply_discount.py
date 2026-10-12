def apply_discount(price: float, discount_pct: float) -> float:
    # try:
    return price - (price * discount_pct / 100)
    # except Exception:
    #     return price


if __name__ == "__main__":
    print(apply_discount(100.0, 10))
    print(apply_discount(100.0))
    print(apply_discount(100.0, "ten"))
