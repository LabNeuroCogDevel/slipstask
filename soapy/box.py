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
        """Fruits in this box should know about the box
        >>> bx = Box(Fruit('apple'),Fruit('kiwi'),Direction.Right,{},'R0')
        >>> bx.updateFruit()
        >>> bx.Stim.name
        'apple'
        >>> bx.Outcome.name
        'kiwi'
        >>> bx.Outcome.box.Stim.name
        'apple'
        """
        self.Stim.SO = SO.Stim
        self.Outcome.SO = SO.Outcome
        self.Stim.box = self.Outcome.box = self

    def score_raw(self, choice: Optional[Direction], isdeval: bool):
        """ score without knowing about particular block
        @param choice - participant selected open direction Left, Right, or None
        @param isdeval - has this box been devalud
        @return score (-1,0,1)
        >>> bx = Box(Fruit('apple'),Fruit('kiwi'), Direction.Left, {}, 'TestBox')
        >>> bx.score_raw(Direction.Left, False)
        1
        >>> bx.score_raw(Direction.Left, True)
        -1
        >>> bx.score_raw(Direction.Right, True)
        0
        >>> bx.score_raw(Direction.Right, False)
        0
        """
        if not choice:
            return 0
        if isdeval:
            if self.Dir == choice:
                return -1
            else:
                return 0
        else:
            if self.Dir == choice:
                return 1
            else:
                return 0

    def score(self, btype: PhaseType, bnum: int, choice: Optional[Direction]):
        """get score for box
        @param btype - blocktype
        @param bnum - block number
        @param choice - direction participant choose. can be None
        @return score (-1,0,1)

        >>> bx = Box(Fruit('apple'),Fruit('kiwi'), Direction.Left, {PhaseType.SOA: [1]}, 'TestBox')
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
        # print(f"# DEBUG: btype {btype} for {bnum} in {self.devalued_blocks}")
        isdeval =  btype in [PhaseType.DD, PhaseType.SOA] and \
           bnum in self.devalued_blocks.get(btype, [])
        return self.score_raw(choice, isdeval)

    def __repr__(self) -> str:
        return f"{self.name}: {self.Stim.name} -> {self.Outcome.name} ({self.Dir})"
