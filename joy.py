"""
Joy
===

Joy is a tiny creative coding library in Python.

BASIC USAGE

An example of using joy:

    >>> from joy import *
    >>>
    >>> c = circle(x=100, y=100, r=50)
    >>> show(c)

The `circle` function creates a new circle and the `show` function
displays it.

PRINCIPLES

Joy follows functional programming approach for its interface. Each
function/class gives a shape and those shapes can be transformed and
combined using other utility functions.

By design, there is no global state in the library.

Joy uses SVG to render the shapes and the shapes are really a very thin
wrapper over SVG nodes. It is possible to use every functionality of SVG,
even if that is not exposed in the API.

COORDINATE SYSTEM

Joy uses a canvas with (0, 0) as the center of the canvas.

By default the size of the canvas is (300, 300).

BASIC SHAPES

Joy supports `circle`, `rectangle` and `line` as basic shapes.

    >>> c = circle(x=100, y=100, r=50)
    >>> r = rectangle(x=0, y=0, w=200, h=200)
    >>> show(c, r)

All basic shapes have default values of all the arguments, making it
easier to start using them.

    >>> c = circle()
    >>> r = rectangle()
    >>> z = line()
    >>> show(c, r, z)

COMBINING SHAPES

The `+` operator is used to combine multiple shapes into a
single shape.

    >>> shape = circle() + rectangle()
    >>> show(shape)

TRANSFORMATIONS

Joy supports `translate`, `rotate` and `scale` transformations.

The `translate` transformation moves the given shape by `x` and `y`.

    >>> c1 = circle(r=50)
    >>> c2 = c1 | translate(x=100, y=0)
    >>> show(c1, c2)

As you've seen the above example, transformations are applied using
the `|` operator.

The `Rotate` transformation rotates a shape anti-clockwise by the specified
angle.

    >>> shape = rectangle() | rotate(angle=45)
    >>> show(shape)

The `Scale` transformation scales a shape.

    >>> shape = circle() | scale(x=1, y=0.5)
    >>> show(shape)

HIGER ORDER TRANSFORMATIONS

Joy supports a transform called `repeat` to apply a transformation multiple times
and combining all the resulting shapes.

    >>> flower = rectangle() | repeat(18, rotate(10))
    >>> show(flower)

JUPYTER LAB INTEGRATION

Joy integrates very well with Jupyter notebooks and every shape is
represented as SVG image by jupyter.
"""
import html
import itertools
import random as random_module
import string

__version__ = "0.3.1"
__author__ = "Anand Chitipothu <anand@fossunited.org>"

SQRT2 = 2**0.5

# Random suffix to avoid conflicts between ids of multiple sketches in the same page
ID_SUFFIX = "".join(random_module.choice(string.ascii_letters+string.digits) for i in range(4))

_shape_counter = itertools.count()


class Shape:
    """Shape is the base class for all shapes in Joy.

    A Shape is an SVG node and supports converting itself into svg text.

    Typically, users do not interact with this class directly, but use it
    through its subclasses.
    """
    def __init__(self, tag, children=None, transform=None, **attrs):
        """Creates a new shape.
        """
        self.tag = tag
        self.children = children
        self.attrs = attrs
        self.transform = None

    def _get_next_shape_id(self):
        id = next(_shape_counter)
        return f"s-{id}-{ID_SUFFIX}" 

    def get_reference(self):
        if not "id" in self.attrs:
            self.attrs["id"] = self._get_next_shape_id()

        attrs = {"xlink:href": "#" + self.id}
        return Shape("use", **attrs)

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>"

    def __getattr__(self, name):
        if not name.startswith("_") and name in self.attrs:
            return self.attrs[name]
        else:
            raise AttributeError(name)

    def apply_transform(self, transform):
        if self.transform is not None:
            transform = self.transform | transform

        shape = self.clone()
        shape.transform = transform
        return shape

    def clone(self):
        shape = object.__new__(self.__class__)
        shape.__dict__.update(self.__dict__)

        # don't share attrs on clone
        # also remove the id as the new nodes gets a new id
        shape.attrs = dict(self.attrs)
        shape.attrs.pop("id", None)
        return shape

    def get_attrs(self):
        attrs = dict(self.attrs)
        if self.transform:
            attrs['transform'] = self.transform.as_str()
        return attrs

    def as_dict(self):
        d = self.get_attrs()
        d['tag'] = self.tag
        if self.children:
            d['children'] = [n.as_dict() for n in self.children]
        return d

    def _svg(self, indent="") -> str:
        """Returns the svg representation of this node.

        This method is used to recursively construct the svg of a node
        and it's children.

            >>> c = Shape(tag='circle', cx=100, cy=100, r=50)
            >>> c._svg()
            '<circle cx="100" cy="100" r="50" />'
        """
        attrs = self.get_attrs()
        if self.children:
            tag_text = render_tag(self.tag, **attrs, close=False)
            return (
                indent + tag_text + "\n" +
                "".join(c._svg(indent + "  ") for c in self.children) +
                indent + "</" + self.tag + ">\n"
            )
        else:
            tag_text = render_tag(self.tag, **attrs, close=True)
            return indent + tag_text + "\n"

    def as_svg(self, width=300, height=300) -> str:
        """Renders this node as svg image.

        The svg image is assumed to be of size (300, 300) unless the
        width and the height arguments are provided.

        Example:

            >>> c = Shape(tag='circle', cx=100, cy=100, r=50)
            >>> print(c.as_svg())
            <svg width="300" height="300" viewBox="-150 -150 300 350" fill="none" stroke="black" xmlns="http://www.w3.org/2000/svg">
              <circle cx="100" cy="100" r="50" />
            </svg>
        """
        return SVG([self], width=width, height=height).render()

    def __add__(self, shape):
        if not isinstance(shape, Shape):
            return NotImplemented
        return Group([self, shape])

    def _repr_svg_(self):
        """Returns the svg representation of this node.

        This method is called by Juputer to render this object as an
        svg image.
        """
        return self.as_svg()

class SVG:
    """SVG renders any svg element into an svg image.
    """
    def __init__(self, nodes, width=300, height=300):
        self.nodes = nodes
        self.width = width
        self.height = height

    def render(self):
        attrs = {
            "tag": "svg",
            "width": self.width,
            "height": self.height,
            "viewBox": f"-{self.width//2} -{self.height//2} {self.width} {self.height}",
            "fill": "none",
            "stroke": "black",
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink"
        }
        svg_header = render_tag(**attrs)+ "\n"
        svg_footer = "</svg>\n"

        # flip the y axis so that y grows upwards
        node = Group(self.nodes) | Scale(sx=1, sy=-1)

        return svg_header + node._svg() + svg_footer

    def _repr_svg_(self):
        return self.render()

    def __str__(self):
        return self.render()

    def __repr__(self):
        return "SVG:{self.nodes}"

class Point:
    """Creates a new Point.

    Point represents a point in the coordinate space and it contains
    attributes x and y.

        >>> p = Point(x=100, y=50)
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, p):
        return isinstance(p, Point) \
            and p.x == self.x \
            and p.y == self.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Circle(Shape):
    """Creates a circle shape.

    Parameters:
        center:
            The center point of the circle.
            Defaults to Point(0, 0) when not specified.

        radius:
            The radius of the circle.
            Defaults to 100 when not specified.

    Examples:

    Draw a circle.

        >>> c = Circle()
        >>> show(c)

    Draw a Circle with radius 50.

        >>> c = Circle(radius=50)
        >>> show(c)

    Draw a circle with center at (100, 100) and radius as 50.

        >>> c = Circle(center=Point(x=100, y=100), radius=50)
        >>> show(c)

    When no arguments are specified, it uses (0, 0) as the center and
    100 as the radius.
    """
    def __init__(self, center=Point(0, 0), radius=100, **kwargs):
        self.center = center
        self.radius = radius

        cx, cy = self.center.x, self.center.y
        super().__init__("circle",
            cx=cx,
            cy=cy,
            r=self.radius,
            **kwargs)

class Ellipse(Shape):
    """Creates an ellipse shape.

    Parameters:
        center:
            The center point of the ellipse. Defaults to (0, 0) when
            not specified.

        width:
            The width of the ellipse. Defaults to 100 when not
            specified.

        height:
            The height of the ellipse. Defaults to 100 when not
            specified.

    Examples:

    Draw an ellipse with center at origin and width of 200 and height of 100:

        >>> r = Ellipse()
        >>> show(r)

    Draw an ellipse having a width of 100 and a height of 50.

        >>> r = Ellipse(width=100, height=50)
        >>> show(r)

    Draw an ellipse centered at (100, 100) and with a width
    of 200 and height of 100.

        >>> r = Ellipse(center=Point(x=100, y=100), width=200, height=100)
        >>> show(r)
    """
    def __init__(self, center=Point(0, 0), width=200, height=100, **kwargs):
        self.center = center
        self.width = width
        self.height = height

        cx, cy = self.center.x, self.center.y
        rx = width/2
        ry = height/2
        super().__init__(
            tag="ellipse",
            cx=cx,
            cy=cy,
            rx=rx,
            ry=ry,
            **kwargs)

class Rectangle(Shape):
    """Creates a rectangle shape.

    Parameters:
        center:
            The center point of the rectangle. Defaults to (0, 0) when
            not specified.

        width:
            The width of the rectangle. Defaults to 200 when not
            specified.

        height:
            The height of the rectangle. Defaults to 100 when not
            specified.

    Examples:

    Draw a rectangle:

        >>> r = Rectangle()
        >>> show(r)

    Draw a square.

        >>> r = Rectangle(width=200, height=200)
        >>> show(r)

    Draw a rectangle centered at (100, 100) and with a width
    of 200 and height of 100.

        >>> r = Rectangle(center=Point(x=100, y=100), width=200, height=100)
        >>> show(r)
    """
    def __init__(self, center=Point(0, 0), width=200, height=100, **kwargs):
        self.center = center
        self.width = width
        self.height = height

        cx, cy = self.center.x, self.center.y
        x = cx - width/2
        y = cy - height/2
        super().__init__(
            tag="rect",
            x=x,
            y=y,
            width=width,
            height=height,
            **kwargs)

class Line(Shape):
    """Basic shape for drawing a line connecting two points.

    Parameters:
        start:
            The starting point of the line. Defaults to (-100, 0) when
            not specified.

        end:
            The ending point of the line. Defaults to (100, 0) when not
            specified.

    Examples:

    Draw a line:

        >>> z = line()
        >>> show(z)

    Draw a line from (0, 0) to (100, 50).

        >>> z = line(start=Point(x=0, y=0), end=Point(x=100, y=50))
        >>> show(z)
    """
    def __init__(self, start=Point(-100, 0), end=Point(100, 0), **kwargs):
        self.start = start
        self.end = end

        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y

        super().__init__("line", x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)

class Group(Shape):
    """Creates a container to group a list of shapes.

    This class is not meant for direct consumption of the users. Users
    are recommended to use `combine` to combine multiple shapes and use
    `translate`, `rotate` and `scale` for doing transformations.

    This creates an svg <g> element.

    Parameters:
        shapes:
            The list of shapes to group.

    Examples:

    Combine a circle and a rectangle.

        >> c = Circle()
        >> r = Rectangle()
        >>> shape = Group([c, r])
        >>> show(shape)

    Shapes can also be combined using the + operator and that creates
    a group implicitly.

        >>> shape = Circle() + Rectangle()
        >>> show(shape)
    """
    def __init__(self, shapes, **kwargs):
        super().__init__("g", children=shapes, **kwargs)

def render_tag(tag, *, close=False, **attrs):
    """Renders a html/svg tag.

        >>> render_tag("circle", cx=0, cy=0, r=10)
        '<circle cx="0" cy="0" r="10">'

    When `close=True`, the tag is closed with "/>".

        >>> render_tag("circle", cx=0, cy=0, r=10, close=True)
        '<circle cx="0" cy="0" r="10" />'

    Underscore characters in the attribute name are replaced with hypens.

        >>> render_tag("circle", cx=0, cy=0, r=10, stroke_width=2)
        '<circle cx="0" cy="0" r="10" stroke-width="2">'
    """
    end = " />" if close else ">"

    if attrs:
        items = [(k.replace("_", "-"), html.escape(str(v))) for k, v in attrs.items() if v is not None]
        attrs_text = " ".join(f'{k}="{v}"' for k, v in items)

        return f"<{tag} {attrs_text}{end}"
    else:
        return f"<{tag}{end}"

class Transformation:
    def apply(self, shape):
        return shape.apply_transform(self)

    def join(self, transformation):
        return TransformationList([self, transformation])

    def __or__(self, right):
        if not isinstance(right, Transformation):
            return NotImplemented
        return self.join(transformation=right)

    def __ror__(self, left):
        if not isinstance(left, Shape):
            return NotImplemented
        return self.apply(shape=left)

class TransformationList(Transformation):
    def __init__(self, transformations):
        self.transformations = transformations

    def join(self, transformation):
        return TransformationList(self.transformations + [transformation])

    def as_str(self):
        # Reversing the transformations as SVG applies them in the
        # reverse order (the rightmost is appled first)
        return " ".join(t.as_str() for t in self.transformations[::-1])

class Translate(Transformation):
    """Creates a new Translate transformation that moves a shape by
    x and y when applied.

    Parameters:
        x:
            The number of units to move in the x direction

        y:
            The number of units to move in the y direction

    Example:

    Translate a circle by (100, 50).

        >>> c = Circle() | Translate(100, 50)
        >>> show(c)
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_str(self):
        return f"translate({self.x} {self.y})"

class Rotate(Transformation):
    """Creates a new rotate transformation.

    When applied to a shape, it rotates the given shape by angle, around
    the anchor point.

    Parameters:

        angle:
            The angle to rotate the shape in degrees.

        anchor:
            The anchor point around which the rotation is performed.

    Examples:

    Rotates a square by 45 degrees.

        >>> shape = Rectangle() | Rotate(angle=45)
        >>> show(shape)

    Rotate a rectangle around its top-left corner and
    combine with itself.

        >>> r1 = Rectangle()
        >>> r2 = r1 | Rotate(angle=45, anchor=(r.point[0]))
        >>> shape = combine(r1, r2)
        >>> show(shape)
    """
    def __init__(self, angle, anchor=Point(0, 0)):
        self.angle = angle
        self.anchor = anchor

    def as_str(self):
        origin = Point(0, 0)
        if self.anchor == origin:
            return f"rotate({self.angle})"
        else:
            return f"rotate({self.angle} {self.anchor.x} {self.anchor.y})"

class Scale(Transformation):
    """Creates a new scale transformation.

    Parameters:
        sx:
            The scale factor in the x direction.

        sy:
            The scale factor in the y direction. Defaults to
            the value of sx if not provided.
    """
    def __init__(self, sx, sy=None):
        if sy is None:
            sy = sx
        self.sx = sx
        self.sy = sy

    def as_str(self):
        return f"scale({self.sx} {self.sy})"

class Repeat(Transformation):
    """Repeat is a higher-order transformation that repeats a
    transformation multiple times.

    Parameters:
        n:
            The number of times to rotate. This also determines the
            angle of each rotation, which will be 360/n.

        transformation:
            The transformation to apply repeatedly.

    Examples:

    Draw three circles:

        >>> shape = Circle(radius=25) | Repeat(4, Translate(x=50, y=0))
        >>> show(shape)

    Rotate a line multiple times:

        >>> shape = Line() | Repeat(36, Rotate(angle=10))
        >>> show(shape)

    Rotate and shrink a line multiple times:

        >>> shape = Line() | Repeat(18, Rotate(angle=10) | Scale(sx=0.9))
        >>> show(shape)
    """
    def __init__(self, n, transformation):
        self.n = n
        self.transformation = transformation

    def apply(self, shape):
        ref = shape.get_reference()
        defs = Shape("defs", children=[shape])

        return defs + self._apply(ref, self.transformation, self.n)

    def _apply(self, shape, tf, n):
        if n == 1:
            return shape
        else:
            result = self._apply(shape, tf, n-1) | tf
            return shape + result

class Cycle(Transformation):
    """
    Rotates the given shape repeatedly and combines all the resulting
    shapes.

    The cycle function is very amazing transformation and it creates
    surprising patterns.

    Parameters:
        n:
            The number of times to rotate. This also determines the
            angle of each rotation, which will be 360/n.

        anchor:
            The anchor point for the rotation. Defaults to (0, 0) when
            not specified.

        s:
            Optional scale factor to scale the shape for each rotation.
            This can be used to grow or shrink the shape while rotating.

        angle:
            Optional angle of rotation. Defaults to 360/n when not
            specified,
    Examples:

    Cycle a line:

        >>> shape = Line() | Cycle()
        >>> show(shape)

    Cycle a square:

        >>> shape = Rectangle() | Cycle()
        >>> show(shape)

    Cycle a rectangle:

        >>> shape = Rectangle(width=200, height=100) | Cycle()
        >>> show(shape)

    Cycle an ellipse:

        >>> e = scale(Circle(), sx=1, sy=0.5)
        >>> show(e | Cycle())

    Create a spiral with shrinking squares:

        >>> shape = Rectangle(width=300, height=300) | cycle(n=72, s=0.92)
        >>> show(shape)
    """
    def __init__(self, n=18, anchor=Point(x=0, y=0), s=None, angle=None):
        self.n = n
        self.angle = angle if angle is not None else 360/n
        self.anchor = anchor
        self.s = s

    def apply(self, shape):
        shapes = [shape | Rotate(angle=i*self.angle, anchor=self.anchor) for i in range(self.n)]
        if self.s is not None:
            shapes = [shape_ | Scale(sx=self.s**i) for i, shape_ in enumerate(shapes)]
        return Group(shapes)

def show(*shapes):
    """Shows the given shapes.

    It also adds a border to the canvas and axis at the origin with
    a light color as a reference.

    Parameters:

        shapes:
            The shapes to show.

    Examples:

    Show a circle:

        >>> show(circle())

    Show a circle and square.

        >>> c = circle()
        >>> s = rect()
        >>> show(c, s)
    """
    markers = [
        Rectangle(width=300, height=300, stroke="#ddd"),
        Line(start=Point(x=-150, y=0), end=Point(x=150, y=0), stroke="#ddd"),
        Line(start=Point(x=0, y=-150), end=Point(x=0, y=150), stroke="#ddd")
    ]
    shapes = markers + list(shapes)
    img = SVG(shapes)

    from IPython.display import display
    display(img)

def circle(x=0, y=0, r=100, **kwargs):
    """Creates a circle with center at (x, y) and radius of r.

    Examples:

    Draw a circle.

        c = circle()
        show(c)

    Draw a circle with radius 50.

        c = circle(r=50)
        show(c)

    Draw a circle with center at (10, 20) and a radius of 50.

        c = circle(x=10, y=20, r=50)
        show(c)
    """
    return Circle(center=Point(x=x, y=y), radius=r, **kwargs)

def rectangle(x=0, y=0, w=200, h=100, **kwargs):
    """Creates a rectangle with center at (x, y), a width of w and a height of h.

    Examples:

    Draw a rectangle.

        r = rectangle()
        show(r)

    Draw a rectangle with width of 100 and height of 50.

        r = rectangle(w=100, h=50)
        show(r)

    Draw a rectangle with center at (10, 20), a width of 100 and a height of 50.

        r = rectangle(x=10, y=20, w=100, h=50)
        show(r)
    """
    return Rectangle(center=Point(x=x, y=y), width=w, height=h, **kwargs)

def ellipse(x=0, y=0, w=200, h=100, **kwargs):
    """Creates an ellipse with center at (x, y), a width of w and a height of h.

    Examples:

    Draw an ellipse.

        r = ellipse()
        show(r)

    Draw an ellipse with a width of 100 and height of 50.

        r = ellipse(w=100, h=50)
        show(r)

    Draw an ellipse with center at (10, 20), a width of 100 and a height of 50.

        r = ellipse(x=10, y=20, w=100, h=50)
        show(r)
    """
    return Ellipse(center=Point(x=x, y=y), width=w, height=h, **kwargs)

def line(x1=None, y1=None, x2=None, y2=None, **kwargs):
    """Creates a line from point (x1, y1) to point (x2, y2).

    Examples:

    Draw a line.

        z = line()

    Draw a line from (10, 20) to (100, 200)

        z = line(x1=10, y1=20, x2=100, y2=200)
    """
    if x1 is None and y1 is None and x2 is None and y2 is None:
        x1, y1 = -100, 0
        x2, y2 = 100, 0
    else:
        pairs = dict(x1=x1, y1=y1, x2=x2, y2=y2)
        missing = [name for name, value in pairs.items() if value is None]
        if missing:
            raise Exception("missing arguments for line: ", ", ".join(missing))

    return Line(start=Point(x1, y1), end=Point(x2, y2), **kwargs)

def point(x, y):
    """Creates a Point with x and y coordinates.
    """
    return Point(x, y)

def polygon(points, **kwargs):
    """Creates a polygon with given list points.

    Example:

        p1 = point(x=0, y=0)
        p2 = point(x=100, y=0)
        p3 = point(x=0, y=100)
        triangle = polygon([p1, p2, p3])
        show(triangle)
    """
    points_str = " ".join(f"{p.x},{p.y}" for p in points)
    return Shape(tag="polygon", points=points_str, **kwargs)

def polyline(points, **kwargs):
    """Creates a polyline with given list points.

    Example:

        p1 = point(x=-50, y=50)
        p2 = point(x=0, y=-25)
        p3 = point(x=0, y=25)
        p4 = point(x=50, y=-50)
        line = polyline([p1, p2, p3, p4])
        show(line)
    """
    points_str = " ".join(f"{p.x},{p.y}" for p in points)
    return Shape(tag="polyline", points=points_str, **kwargs)

def translate(x=0, y=0):
    """Translates a shape.

    Examples:

    Translate a shape by 10 units in x direction.

        shape = circle() | translate(x=10)

    Translate a shape by 10 units in y direction.

        shape = circle() | translate(y=10)

    Translate a shape by 10 units in x direction and 20 units in y direction.

        shape = circle() | translate(x=10, y=20)
    """
    return Translate(x=x, y=y)

def scale(s=None, x=1, y=1):
    """Scales a shape.

    Examples:

    Scale a shape in both x and y directions:

        shape = circle() | scale(0.5)

    Scale a shape in only in x direction:

        shape = circle() | scale(x=0.5)

    Scale a shape in only in y direction:

        shape = circle() | scale(y=0.5)

    Scale a shape differently in x and y directions:

        shape = circle() | scale(x=0.5, y=0.75)
    """
    if s is not None:
        return Scale(sx=s, sy=s)
    else:
        return Scale(sx=x, sy=y)

def rotate(angle):
    """Rotates a shape.

    Examples:

    Rotate a shape by 30 degrees

        shape = line() | rotate(30)
    """
    return Rotate(angle)

def repeat(n, transformation):
    """Repeats a transformation multiple times on a shape.

    Examples:

    Repeatly rotate a line 9 times by 10 degrees.

        shape = line() | repeat(9, rotate(10))
    """
    return Repeat(n, transformation)

def combine(shapes):
    """The combine function combines a list of shapes into a single shape.

    Example:
        >>> shapes = [circle(r=50), circle(r=100), circle(r=150)]
        >>> shape = combine(shapes)
        >>> show(shape)
    """
    return Group(shapes)

def color(r, g, b, a=None):
    """Creates a color with given r g b values.

    Parameters:

    r - the red component of the color, allowed range is 0-255.
    g - the green component of the color, allowed range is 0-255.
    b - the blue component of the color, allowed range is 0-255.
    a - optional argument to indicate the transparency or the
        alpha value. The allowed range is 0-1.
    """
    if a is None:
        return f"rgb({r}, {g}, {b})"
    else:
        return f"rgba({r}, {g}, {b}, {a})"

def random(a=None, b=None):
    """Creates a random number.

    The random function can be used in three ways:

        random() # returns a random number between 0 and 1
        random(n) # returns a random number between 0 and n
        random(n1, n2) # returns a random number between n1 and n2

    Examples:

        >>> random()
        0.4336206360591218
        >>> random(10)
        1.436301598755494
        >>> random(5, 10)
        7.471950621969087
    """
    if a is None and b is None:
        return random_module.random()
    elif a is not None and b is None:
        return a * random_module.random()
    else:
        delta = b - a
        return a + delta * random_module.random()
