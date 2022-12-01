from const import GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS
from main_changes import get_changes
from main_perenosi import get_perenosi


get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS)
get_perenosi(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, "2022-09-26")