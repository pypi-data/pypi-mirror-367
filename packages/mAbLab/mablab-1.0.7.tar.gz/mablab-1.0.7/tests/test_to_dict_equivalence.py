import sys
import os
import unittest

# Add the root directory to the Python path so mAbLab can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mAbLab import Mab

LC_SEQ = 'DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDVATYYCQRYNRAPYTFGQGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC'
HC_SEQ = 'EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'
HC2_SEQ = 'DKTHTCPPCPAPEAAGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSREEMTKNQVSLWCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'

class TestToDictEquivalence(unittest.TestCase):
    def setUp(self):
        self.mab = Mab(hc1_aa_sequence=HC_SEQ, hc2_aa_sequence=HC_SEQ, lc1_aa_sequence=LC_SEQ, lc2_aa_sequence=LC_SEQ)

    def test_ch2_annotation_kabat_equivalence(self):
        # Direct attribute access
        direct = self.mab.hc1.ch2.annotation.kabat
        # Dict access
        dict_access = self.mab.to_dict()["hc1"]["ch2"]["annotation"]["kabat"]
        self.assertEqual(direct, dict_access)

    def test_ch2_annotation_imgt_equivalence(self):
        direct = self.mab.hc1.ch2.annotation.imgt
        print(direct)
        print('/n')
        dict_access = self.mab.to_dict()["hc1"]["ch2"]["annotation"]["imgt"]
        print(dict_access)
        self.assertEqual(direct, dict_access)

    def test_lc1_vl_numbering_eu_equivalence(self):
        direct = self.mab.lc1.vl.numbering.eu
        dict_access = self.mab.to_dict()["lc1"]["vl"]["numbering"]["eu"]
        self.assertEqual(direct, dict_access)

    def test_lc2_cl_annotation_martin_equivalence(self):
        direct = self.mab.lc2.cl.annotation.martin
        dict_access = self.mab.to_dict()["lc2"]["cl"]["annotation"]["martin"]
        self.assertEqual(direct, dict_access)

if __name__ == "__main__":
    unittest.main()
