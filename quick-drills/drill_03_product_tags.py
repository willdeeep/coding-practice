def add_tag(product: dict, tag: str, tags=[]):
    tags.append(tag)
    product["tags"] = tags
    return product


if __name__ == "__main__":
    p1 = add_tag({"sku": "A1"}, "sale")
    p2 = add_tag({"sku": "B2"}, "clearance")
    print(p1)
    print(p2)
        