import pytest

@pytest.fixture(scope='module')
def initRun(self):
    print('init')

class Testfixture1(): 
    @pytest.fixture(scope='class')
    def firstRun(self):
        print('class')

    @pytest.fixture(scope='function')
    def secondRun(self):
        print('function')

    def getdata(self, num):
        print(num)

    def testFixture1(self, firstRun, secondRun):
        print('test body')
        self.getdata(3)
        
    def testFixture2(self, firstRun, secondRun):
        print('test2 body')