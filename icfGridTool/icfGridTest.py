#!/usr/bin/env python
from icfGridLib import *
import unittest

class TestConversionFunctions(unittest.TestCase):
    def testGetRaw(self):
        tr=getRaw(True,BooleanType)
        self.assertEqual(tr,1)
        fa=getRaw(False,BooleanType)
        self.assertEqual(fa,0)
        st=getRaw("Hello",StringType)
        self.assertEqual(st,"Hello")
        i=getRaw(1,IntType)
        self.assertEqual(i,1)

    def testSetRaw(self):
        b=setRaw("hello",StringType)
        self.assertEqual(b,"hello")
        b=setRaw("1000",IntType)
        self.assertEqual(b,1000)
        b=setRaw(" 1000 ",IntType)
        self.assertEqual(b,1000)
        self.assertRaises(ValueError,setRaw,"abcd",IntType)
        b=setRaw("1",BooleanType)
        self.assertEqual(b,1)
        b=setRaw("0",BooleanType)
        b=setRaw(" 1 ",BooleanType)
        self.assertEqual(b,1)
        self.assertRaises(ValueError,setRaw,"2",BooleanType)
        self.assertRaises(ValueError,setRaw,"abcd",BooleanType)
        self.assertRaises(ValueError,setRaw,12,StringType)

    def testCastorReplace(self):
        if "CASTOR_HOME" in os.environ:
            del os.environ["CASTOR_HOME"]
        self.assertRaises(Exception,castorReplace,"~")
        self.assertRaises(Exception,castorReplace,"~/hello")
        self.assertEqual(castorReplace("hello"),"hello")
        os.environ["CASTOR_HOME"]="test"
        self.assertEqual(castorReplace("test"),"test")
        self.assertEqual(castorReplace("~test"),"testtest")
        p="~Hello"
        castorReplace(p)
        self.assertEqual(p,"~Hello")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConversionFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
