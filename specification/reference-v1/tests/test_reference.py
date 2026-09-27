import json, unittest
from decimal import Decimal
from pathlib import Path
import reference_core as core

class ReferenceContracts(unittest.TestCase):pass
for vector in json.loads((Path(__file__).parents[1]/'fixtures/vectors.json').read_text()):
    def run(self,v=vector):
        fn=getattr(core,v['function'])
        if 'error' in v:
            with self.assertRaises(core.ContractError) as error:fn(*v['args'])
            self.assertEqual(error.exception.code,v['error'])
        else:
            actual=fn(*v['args'])
            if isinstance(actual,Decimal):actual=format(actual,'f')
            self.assertEqual(actual,v['expected'])
    run.__doc__=vector['title']
    setattr(ReferenceContracts,'test_'+vector['id'].replace('-','_'),run)

class Canonicalisation(unittest.TestCase):
    def test_object_order(self):self.assertEqual(core.canonical_hash({'b':2,'a':1}),core.canonical_hash({'a':1,'b':2}))
    def test_array_order(self):self.assertNotEqual(core.canonical_hash([1,2]),core.canonical_hash([2,1]))
    def test_nonfinite(self):
        with self.assertRaises(ValueError):core.canonical_hash({'v':float('nan')})
