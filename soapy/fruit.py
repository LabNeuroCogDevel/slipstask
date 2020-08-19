from soapy import image_path
from soapy.task_types import PhaseType, SO
# from box import Box
#  NB. circular import: fruit can point to the box it's part of


class Fruit:
    """Fruits or Veggies or Animals -- thing in or on the box
    also is a stimulus or an outcome (SO)
    cyclic link to Box class. Box contains fruits. Fruit can point back to box
    when box is made, it will set SO, pair, and box slots
    >>> import os
    >>> f = Fruit('apple')
    >>> f.name
    'apple'
    >>> os.path.basename(f.image)
    'apple.png'
    """
    name: str
    image: str
    SO: SO
    # get direction and devalued_blocks from box.*
    box: 'Box'

    def __init__(self, name):
        self.name = name
        self.image = image_path(f"{name}.png")

    def __repr__(self) -> str:
        return f"{self.name}: {self.SO} {self.box.Dir} " +\
            ",".join(["%d" % x for x in self.box.devalued_blocks.get(PhaseType.SOA, 0)])
