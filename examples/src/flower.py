
s = circle(x=125, r=10) + circle(x=125, r=5)
shape = s| repeat(20,  scale(0.85)|rotate(5)) | repeat(36, rotate(10))
show(shape)