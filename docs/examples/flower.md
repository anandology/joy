# Flower

<div class="example">

<!--INCLUDE src/flower.py -->
```python
s = circle(x=135, r=10) + circle(x=135, r=5)
shape = s| repeat(20,  scale(0.85)|rotate(5)) | repeat(36, rotate(10))
show(shape)
```
<!-- ENDINCLUDE -->

<div class="output image"><img src="../images/flower.svg"></div>

</div>