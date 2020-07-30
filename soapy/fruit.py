from soapy.task_types import PhaseType, SO
# from box import Box
#  NB. circular import: fruit can point to the box it's part of


class Fruit:
    """Fruits or Veggies or Animals -- thing in or on the box"""
    name: str
    image: str
    SO: SO
    # get direction and devalued_blocks from box.*
    pair: 'Fruit'
    box: 'Box'

    def __init__(self, name):
        self.name = name
        self.image = "static/images/%s.png" % name

    def __repr__(self) -> str:
        return f"{self.name}: {self.SO} {self.box.Dir} " +\
            ",".join(["%d" % x for x in self.box.devalued_blocks.get(PhaseType.SOA, 0)])
