
def find(lis, target):
    try:
        lis.index(target)
        return True
    except ValueError as v:
        return False
    return False


def findIndex(lis, target):
    index = -1
    try:
        index = lis.index(target)
    except ValueError as v:
        return index
    return index

def getK(num1,start1,end1,num2,start2,end2,k):
    len1=end1-start1+1
    len2=end2-start2+1
    def min(s1,s2):
        if s1>s2:
            return s2
        else:
            return s1
    if len1>len2:
        return getK(num2,start2,end2,num1,start1,end1,k)
    if len1==0:
        return num2[start2+k-1]
    if k==1:
        return min(num1[start1],num2[start2])
    i=start1+min(k//2,len1)-1
    j=start2+min(k//2,len2)-1
    if num1[i]>num2[j]:
        return getK(num1,start1,end1,num2,j+1,end2,k-(j-start2+1))
    else:
        return getK(num1, i+1,end1, num2, start2, end2, k - (i - start1+1))

def findMedianSortedArrays(nums1, nums2):
    n=len(nums1)
    m=len(nums2)
    left = (n + m + 1) // 2
    right = (n + m + 2) // 2
    return (getK(nums1, 0, n-1, nums2,0, m-1, left)+getK(nums1, 0, n-1, nums2,0, m-1, right))/2

def treenode(start,end):
    if start>end:
        return [None]
    allThree=[]
    for i in range(start,end+1):
        leftThree=treenode(start,i-1)
        rightThree=treenode(i+1,end)
        for l in leftThree:
            for r in rightThree:
                pass
                # currTree = TreeNode(i)
                # currTree.left


if __name__ == '__main__':
    print(findMedianSortedArrays([1,3],[2,6,7,8]))