def beside(a, b):
    a1 = a | scale(x=0.5) | translate(x=-75)
    b1 = b | scale(x=0.5) | translate(x=75)
    return a1+b1

def below(a, b):
    a1 = a | scale(y=0.5) | translate(y=75)
    b1 = b | scale(y=0.5) | translate(y=-75)
    return a1+b1

def quartlet(a, b, c, d):
    return below(
        beside(a, b),
        beside(c, d)
    )

p = rectangle(w=300, h=300) | repeat(100, scale(0.92)|rotate(5))
q = p | scale(x=-1)

shape = quartlet(
    p, q,
    q, p)

show(shape)
