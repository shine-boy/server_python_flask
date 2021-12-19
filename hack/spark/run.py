
from pyspark import SparkContext
from pyspark import SparkConf
conf=SparkConf().setAppName("testProject").setMaster("local[*]")
sc=SparkContext.getOrCreate(conf)

if __name__ == '__main__':
    rdd = sc.parallelize(["Hello hello", "Hello New York", "York says hello"])
    def f(x,y):
        print(x)
        print(y)
        return x+y
    resultRDD = (rdd
                 .flatMap(lambda sentence: sentence.split(" "))
                 .map(lambda word: word.lower())
                 .map(lambda word: (word, 1))  # 将word映射成(word,1)
                 .reduceByKey(f)
                 )  # reduceByKey对所有有着相同key的items执行reduce操作
    print(resultRDD.collect())


