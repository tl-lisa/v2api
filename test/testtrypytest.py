import pytest

@pytest.fixture(scope='module')
def initRun():
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

    def testFixture1(self, initRun, firstRun, secondRun):
        print('test body')
        
        
    def testFixture2(self, initRun, firstRun, secondRun):
        print('test2 body')
       