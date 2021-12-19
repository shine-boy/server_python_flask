

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

