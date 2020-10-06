import pytest
from soapy.task_types import Direction, PhaseType, TrialType
import soapy
import soapy.info
import soapy.seeded


class TestScore:

    def test_TimingFileScore(self):
        allDD = soapy.seeded.timing_path(PhaseType.DD)
        firstDD = allDD[0]  # ~DD/1024062378.csv~
        # DD/6/1135626388.csv # 2020-10-05
        # ,phase,ttype,blocknum,trial,LR1,deval,LR2,onset,dur,end,cor_side
        # 0,PhaseType.DD,TrialType.GRID,1,-1,L1,False,R2,3.0,5.0,8.0,
        # 1,PhaseType.DD,TrialType.SHOW,1,0,L0,False,,8.0,2.0,10.0,L
        # 2,PhaseType.DD,TrialType.ITI,1,0,L0,False,,10.0,5.0,15.0,
        # 3,PhaseType.DD,TrialType.SHOW,1,1,L2,False,,15.0,2.0,17.0,L
        ffi = soapy.info.FabFruitInfo(timing_files=[firstDD])
        ffi.set_names(soapy.read_img_list('fruits'))
        allbx = [b.name for b in ffi.boxes]
        deval_bx = ffi.boxes[allbx.index("R1")]

        score = deval_bx.score(PhaseType.ID, 3, Direction.Right)
        assert score == 1

        score = deval_bx.score(PhaseType.ID, 3, Direction.Left)
        assert score == 0

        score = deval_bx.score(PhaseType.ID, 3, None)
        assert score == 0

        score = deval_bx.score(PhaseType.DD, 3, Direction.Left)
        assert score == 0

        score = deval_bx.score(PhaseType.DD, 3, None)
        assert score == 0

        score = deval_bx.score(PhaseType.DD, 3, Direction.Right)
        assert score == -1


    def test_GenScore(self):
        ffi = soapy.info.FabFruitInfo()
        ffi.set_names(soapy.read_img_list('fruits'))
        allbx = [b.name for b in ffi.boxes]
        bx = ffi.boxes[allbx.index("R1")]

        blk = bx.devalued_blocks[PhaseType.DD][0]

        score = bx.score(PhaseType.ID, blk, Direction.Right)
        assert score == 1

        score = bx.score(PhaseType.ID, blk, Direction.Left)
        assert score == 0

        score = bx.score(PhaseType.ID, blk, None)
        assert score == 0

        score = bx.score(PhaseType.DD, blk, Direction.Right)
        assert score == -1

        score = bx.score(PhaseType.DD, blk, Direction.Left)
        assert score == 0

        score = bx.score(PhaseType.DD, blk, None)
        assert score == 0
