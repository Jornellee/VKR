from datetime import date
import pendulum

from const import get_perenosi_date_range


today = pendulum.now()
d1 = today.start_of("week")
d2 = d1.add(weeks=1)
d1 = d1.strftime('%Y.%m.%d')
d2 = d2.strftime('%Y.%m.%d')
print(d1, d2)

get_perenosi_date_range(pendulum.now())
print (get_perenosi_date_range(pendulum.now()))