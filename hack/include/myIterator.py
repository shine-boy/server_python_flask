from collections.abc import Iterator,Generator
class MyIterator(Iterator):
    def __init__(self,lis):
        self.lis=[]
        if isinstance(lis,Iterator):
            self.lis.append(lis)
        elif isinstance(lis, Generator):
                self.lis.append(lis)
        else:
            self.lis.append(iter(lis))
        self.index=0

    def __iter__(self):
        return self

    def append(self,lis):
        if isinstance(iter([]),Iterator):
            self.lis.append(lis)
        else:
            self.lis.append(iter(lis))

    def __next__(self):
        try:
            return next(self.lis[self.index])
        except StopIteration as e:
            self.index += 1
            if self.index>=len(self.lis):
                raise StopIteration
            else:
                return self.__next__()
