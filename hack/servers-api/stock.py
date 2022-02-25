
from serverApi import Response, ServersApi


class Stock(ServersApi):

    def __init__(self, app):
        ServersApi.__init__(app)

    @Response('/test1')
    def test(self):
        pass