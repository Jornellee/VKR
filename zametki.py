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



# сделать красиво сообщения (enter)
# придумать сообщение "учеба начинается со след недели"


# переделать расчет учебы (начало/конец) (новая табличка в бд) 










# потом
func([1,4,3]) # True
func([1,4,4]) # True


    
