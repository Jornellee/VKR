from const import GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS
from main_changes import get_changes
from main_perenosi import get_perenosi
import pendulum


# get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS,  pendulum.local(2023,3,1))
get_perenosi(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, pendulum.local(2023,2,19))