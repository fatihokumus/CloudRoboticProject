import math
from pydstarlite import dstarlite, utility


robots = ['a1', 'a2', 'a3']
goals = ['b1', 'b2', 'b3','b4']

#kombinasyon matrisi
combin = []

#hangi dizi daha az ise o kadar atama yapılacağı için aşağıdaki temp değişkenler kullanılacak.
temp1 = []
temp2 = []

#Atama sayısı gruplardaki en az sayı kimdesyse o kadar olacağı için ayarlama yaptık
if len(robots)>len(goals):
    temp1 = goals
    temp2 = robots
else:
    temp1 = robots
    temp2 = goals


#İlk olarak kombinasyon matrisi oluşturulur.
for i in range(len(temp1)):
    satir = []
    for k in range(len(temp2)):
        satir.append([temp1[i], temp2[k]])
    combin.append(satir)



#kaç sütunlu
width = len(combin[:])

#kaç satırlı
height = len(combin[0][:])




#Öncelikle Olasılık Matrisi oluşturulur. matrisin n x m boyutundadır. r=robot sayısı h=hedef saysı olarak alırsak;
# eğer r < h is n=h^r ve m=r olur.
# eğer r > h is n=r^h ve m=h olur.
# eğer r = h is n=r^r ve m=r olur.

#Olasılık matrisi kaç satırlı olacak
l = int(math.pow(height, width-1))


#Olasılık matrisini oluştur. İlk sütun değerlerini ata. diğer sütunlara 1 ata.
prob = []
for i in range(height):
    for j in range(l):
        satir = []
        satir.append(combin[0][i])
        for k in range(width-1):
            satir.append('1')
        prob.append(satir)


#Olasılık matrisinin diğer sütunlarının verilerini ata.
for i in range(width-1):
    sutun = i+1
    m = int(math.pow(height, width - 1 - sutun))
    satir = 0
    for k in range(int(len(prob)/m)):
        for ss in range(m):
            prob[satir][sutun] = combin[sutun][k % height]
            satir = satir + 1


num=0
for row in range(len(prob)):
    row = prob[num]
    comp = False
    for col in row:
        el = [x for x in row if x[1] == col[1]]
        if(len(el)>1):
            comp = True
    if comp == True:
        prob.remove(row)
        num=num-1
    num = num+1

for j in prob:
    print(j)



GRAPH, START, END = utility.grid_from_string("""
    ..........
    ...######.
    .......A#.
    ...######.
    ...#....#.
    ...#....#.
    ........#.
    ........#.
    ........#Z
    ........#.
    """)
dstar = dstarlite.DStarLite(GRAPH, START, END)
path = [p for p, o, w in dstar.move_to_goal()]

print(path)