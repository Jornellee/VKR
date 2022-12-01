n = 6;
everyweek = [1,2,3,1,2,3];

print(everyweek)
print(list(enumerate(everyweek)))


s = 0;
j = 0;
for (i, x) in enumerate(everyweek):
    if s<=n:
        s += x
        j = i

print(j)