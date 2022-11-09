from tabulate import tabulate

import exercise_2

dicts_list = exercise_2.host_range_ping()
print(tabulate(dicts_list, headers='keys', tablefmt="pipe", stralign="center"))
