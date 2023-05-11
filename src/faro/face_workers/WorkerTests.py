import unittest

class WorkerTest(unittest.TestCase):
    def __init__(self,testName,workerName : str):
        super(WorkerTest,self).__init__(testName)
        self.workerName = workerName
    def setUp(self) -> None:
