def printype(var):
    print(var, type(var))


def printype_symbol(var, symbol="*"):
    print()
    print(80*symbol)
    print(var, type(var), sep="\n")
    print(80*symbol)
    print()


def typerint(var):
    print(type(var), var)


def typerint_symbol(var, symbol="*"):
    print()
    print(80*symbol)
    print(type(var), var, sep="\n")
    print(80*symbol)
    print()


if __name__ == "__main__":
    printype_symbol("test")
    typerint_symbol(4.2, "#")