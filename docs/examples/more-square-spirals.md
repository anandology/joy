# More Square Spirals

This is an extensions of [Square Spiral](square-spiral.md) example.

<div class="example">

<!--INCLUDE src/more-square-spirals.py -->
```python
p = rectangle(w=300, h=300) | repeat(100, scale(0.92)|rotate(5))
q = p | scale(x=-1)

shape = quartlet(
    p, q,
    q, p)

show(shape)
```
<!-- ENDINCLUDE -->

<div class="output image"><img src="../images/more-square-spirals.svg"></div>

</div>
