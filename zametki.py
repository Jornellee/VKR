def func(array):
    left, right = array[:len(array)//2], array[len(array)//2:]
    print (left) 
    print (right)
    print (left == right)
    return left == right


func([1,4,1,4]) # False
func([1,4,2,4]) # True
func([1,4,2,3]) # True
func([2,4,2,3]) # True
func([2,4,2,4]) # False
func([1,1]) # False
func([1,2]) # True
func([1,2,3, 1,2,4]) # True
func([1,2,3, 1,2,3]) # False
func([1,2,3,4, 1,2,3,4]) # False
func([1,2,3,5, 1,2,3,4]) # True

# модуль оповещений о начале сессии
# подумать как выводить если пара была еженедельной, а стало две черезнедельных, 
#что делать если преподаватель хочет получать рассылку своего расписания и группы, которую он курирует 








# потом
func([1,4,3]) # True
func([1,4,4]) # True


    
