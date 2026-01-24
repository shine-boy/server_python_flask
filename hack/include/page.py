from hack.include.list import findIndex

class Page:
    def __init__(self,page=None):
        if page is None:
            page = {
                "pageSize": 10,
                "current": 1
            }
        else:
            if page.get("pageSize") is None:
                page["pageSize"] = 10
            if page.get("current") is None or page.get("current") == 0:
                page["current"] = 1
            # page["pageSize"] = int(page.get("pageSize"))
            # page["current"] = int(page.get("current"))
        self.page=page


class Sort:
    def __init__(self, sort=None):
        if sort is None:
            sort = [("date", -1)]
        else:
            sortKey = sort.get('sort') or 'date'
            order = sort.get('order') or -1
            ascend = ['ascend', 1]
            # descend = ['descend', -1]
            if findIndex(ascend, order) > -1:
                order = 1
            else:
                order = -1
            sort = [(sortKey, order)]
        self.sort = sort


if __name__ == '__main__':
    f = {"name": 1}
    g = f.get('names') or 'time'
    print([1].index(2))
