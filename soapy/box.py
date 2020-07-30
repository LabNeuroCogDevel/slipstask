from typing import Optional
from soapy.task_types import DevalDict, Direction, SO, PhaseType
from soapy.fruit import Fruit


class Box:
    """Box with an outside (stim) and inside (outcome)"""
    def __init__(self, Stim: Fruit, Outcome: Fruit,
                 Dir: Direction, devalued_blocks: DevalDict,
                 name: str):
        self.Stim = Stim
        self.Outcome = Outcome
        self.Dir = Dir
        self.devalued_blocks = devalued_blocks
        self.name = name
        # like L0 to R2

    def updateFruit(self):
        "Fruits in this box should know about the box"
        self.Stim.SO = SO.Stim
        self.Stim.pair = self.Outcome
        self.Outcome.SO = SO.Outcome
        self.Outcome.pair = self.Stim
        self.Stim.box = self.Outcome.box = self

    def score(self, btype: PhaseType, bnum: int, choice: Optional[Direction]):
        """get score for box
        @param btype - blocktype
        @param bnum - block number
        @param choice - direction participant choose. can be None
        @return score (-1,0,1)

        >>> bx = Box(Fruit('s'),Fruit('o'), Direction.Left, {PhaseType.SOA: [1]}, 'TestBox')
        >>> bx.score(PhaseType.ID, 1, Direction.Left)
        1
        >>> bx.score(PhaseType.ID, 1, Direction.Right)
        0
        >>> bx.score(PhaseType.SOA, 1, Direction.Right)
        0
        >>> bx.score(PhaseType.SOA, 1, Direction.Left)
        -1
        >>> bx.score(PhaseType.SOA, 3, Direction.Left)
        1
        >>> bx.score(PhaseType.SOA, 3, None)
        0
        """
        if not choice:
            return 0
        if btype in [PhaseType.DD, PhaseType.SOA] and bnum in self.devalued_blocks[btype]:
            if self.Dir == choice:
                return -1
            else:
                return 0
        else:
            if self.Dir == choice:
                return 1
            else:
                return 0

    def __repr__(self) -> str:
        return f"{self.name}: {self.Stim.name} -> {self.Outcome.name} ({self.Dir})"
