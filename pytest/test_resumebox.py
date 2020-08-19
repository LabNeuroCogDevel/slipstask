import pytest
import soapy
import soapy.info
import soapy.seeded
from soapy.task_types import Direction, PhaseType, TrialType
from soapy import DEFAULT_PHASES, read_img_list


def bnames(boxes):
    x = [f"{x}" for x in boxes]
    sorted(x)
    return "\n".join(x)

class TestResumeBox:

    def test_MRvsNot(self, tmpdir):

        p = PhaseType.DD
        settings = {p: DEFAULT_PHASES[p]}
        nomr = soapy.seeded.single_phase(p, 12345, 0, 0, settings)
        nomr = soapy.seeded.update_boxes(nomr, 'fruits', tmpdir.realpath())
        nomr_bnames = bnames(nomr.boxes)

        # makes box file
        assert tmpdir.join("boxes.txt").check()

        mr = soapy.seeded.single_phase(p, 54321, 0, 1, settings)
        mr.set_names(read_img_list('fruits'))
        # make sure boxes are not the same initially
        # otherwise update_boxes has nothing to do
        assert bnames(mr.boxes) != nomr_bnames

        # but are the same now
        mr = soapy.seeded.update_boxes(mr, 'fruits', tmpdir.realpath())
        assert bnames(mr.boxes) == nomr_bnames
        

        ID = soapy.seeded.single_phase(PhaseType.ID, 543, 0, 0, settings)
        ID.set_names(read_img_list('fruits'))
        # make sure boxes are not the same initially
        # otherwise update_boxes has nothing to do
        assert bnames(ID.boxes) != nomr_bnames

        # but are the same now
        ID = soapy.seeded.update_boxes(ID, 'fruits', tmpdir.realpath())
        assert bnames(ID.boxes) == nomr_bnames
