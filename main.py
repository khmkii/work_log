import config
import csv
import datetime
from entry import Entry
import os
import platform
import re


"""add a clear screen function to tidy of the presentation of data"""

dir_path = config.config['DIR_PATH']
filename = config.config['FILENAME']

file_path = os.path.join(dir_path, filename)

match_date_string = config.config['MATCH_DATE_STRING']


def validate_date(date_string):
    if re.match(match_date_string, date_string):
        try:
            datetime.datetime.strptime(date_string, '%d/%m/%Y')
            return date_string
        except ValueError:
            return None
    else:
        return None


def validate_time_spent(time_spent_string):
    try:
        int(time_spent_string)
        return time_spent_string
    except ValueError:
        return None


def add_entry(entry_list_to_add):
    with open(file_path, 'a', newline='') as file:
        csv_writer = csv.writer(file, delimiter=',')
        csv_writer.writerow(entry_list_to_add)


def build_search_list():
    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f)
        search_list = []
        for row in csv_reader:
            try:
                search_list.append(Entry(*row))
            except TypeError:
                continue
        return search_list


def delete_entry(entry_to_delete):
    all_entries = build_search_list()
    for i, o in enumerate(all_entries):
        if (o.date == entry_to_delete.date and o.job == entry_to_delete.job and
                o.time == entry_to_delete.time and o.notes == entry_to_delete.notes):
            del all_entries[i]
    with open(file_path, 'w') as fi:
        csv_writer = csv.writer(fi, delimiter=',')
        rows = []
        for entry in all_entries:
            rows.append([getattr(entry, x) for x in [entry.date, entry.job, entry.time, entry.notes]])
        for row in rows:
            csv_writer.writerow(row)


def expression_search(reg_exp):
    reg_exp = r'{}'.format(reg_exp)
    list_to_expression_search = build_search_list()
    expression_query_list = []
    for taski in list_to_expression_search:
        if re.search(reg_exp, taski.job) is not None or re.search(reg_exp, taski.notes) is not None:
            expression_query_list.append(taski)
        else:
            print(reg_exp)
    return expression_query_list


def string_search(search_string):
    list_to_search = build_search_list()
    string_query_list = []
    list_of_search_string = search_string.lower().split()
    for task in list_to_search:
        for word in list_of_search_string:
            if word in task.job.lower() or word in task.notes.lower():
                string_query_list.append(task)
                break
    return string_query_list


def time_search(base_time, range_time):
    list_to_time_search = build_search_list()
    time_query_list = []
    if int(range_time) == 0:
        for taskobj in list_to_time_search:
            if int(taskobj.time) == int(base_time):
                time_query_list.append(taskobj)
    else:
        bottom_range = int(base_time) - int(range_time)
        top_range = int(base_time) + int(range_time)
        for taskobj in list_to_time_search:
            if bottom_range <= int(taskobj.time) <= top_range:
                time_query_list.append(taskobj)
    return time_query_list


def date_search(specific_date=None, range_of_dates=None):
    date_query_list = []
    list_to_date_search = build_search_list()
    if specific_date is not None:
        for taskobj in list_to_date_search:
            if taskobj.date == specific_date:
                date_query_list.append(taskobj)
    if range_of_dates is not None:
        start_date = datetime.datetime.strptime(range_of_dates[0], config.config['DATE_FMT'])
        end_date = datetime.datetime.strptime(range_of_dates[1], config.config['DATE_FMT'])
        if start_date < end_date:
            for taskobj in list_to_date_search:
                date_to_check = datetime.datetime.strptime(taskobj.date, config.config['DATE_FMT'])
                if start_date <= date_to_check <= end_date:
                    date_query_list.append(taskobj)
        else:
            return None
    return date_query_list


def print_search_result(result_obj):
    print('Date: ' + result_obj.date)
    print('Job: ' + result_obj.job)
    print('Time Spent: ' + result_obj.time + ' minutes')
    print('Notes: ' + result_obj.notes + '\n')


def make_new_entry(task_date=None, task_job=None, task_minutes=None, task_notes=None):
    if task_date is None:
        while True:
            task_date = input("Enter date as dd/mm/yyyy > ")
            if validate_date(task_date):
                break
            else:
                print("Date must be in the form 'dd/mm/yyyy', and be a valid"
                      " day, month and year combination ")
    if task_job is None:
        task_job = input("Enter job description > ")
    if task_minutes is None:
        while True:
            task_minutes = input("Enter time spent in minutes > ")
            if validate_time_spent(task_minutes):
                break
            print("Time spent must be a number of minutes > ")
    if task_notes is None:
        task_notes = input("Enter task notes > ")
    task_list = [task_date, task_job, task_minutes, task_notes]
    return task_list


def big_function(results):
    print("Search generated {} results".format(len(results)))
    exit_string_search = True
    while exit_string_search:
        for result in results:
            print('\n')
            print_search_result(result)
            action = input("Do you want to edit this entry ('E')\ndelete this entry('X') "
                           " see the next entry ('N')\nor stop reviewing"
                           " the searched entries ('B') > ").upper().strip()
            if action == 'E':
                edit_type = input("You can rewrite the entire entry ('1') or edit the date ('2')\n"
                                  " the task/job name ('3'), the time spent ('4')\nor the "
                                  "notes for this entry ('5')\n"
                                  "make your selection please > ").upper().strip()
                if edit_type == '1':
                    delete_entry(result)
                    add_entry(make_new_entry())
                    results.remove(result)
                    print('Entry has been updated')
                    if len(results) == 0:
                        exit_string_search = False
                        print('No results left to look at')
                    else:
                        continue
                elif edit_type == '2':
                    print("Current date is {}, go ahead and make your edit".format(result.date))
                    new_entry_list = make_new_entry(
                        task_job=result.job, task_minutes=result.time, task_notes=result.notes
                    )
                    delete_entry(result)
                    result.date = new_entry_list[0]
                    add_entry(new_entry_list)
                    print('Entry has been updated')
                elif edit_type == '3':
                    print("Current job is {}, go ahead and make your edit".format(result.job))
                    new_entry_list = make_new_entry(
                        task_date=result.date, task_minutes=result.time, task_notes=result.notes
                    )
                    delete_entry(result)
                    result.job = new_entry_list[1]
                    add_entry(new_entry_list)
                    print('Entry has been updated')
                elif edit_type == '4':
                    print("Current time spent is {} minutes, "
                          "go ahead and make your edit".format(result.time))
                    new_entry_list = make_new_entry(
                        task_date=result.date, task_job=result.job, task_notes=result.notes
                    )
                    delete_entry(result)
                    result.time = new_entry_list[2]
                    add_entry(new_entry_list)
                    print('Entry has been updated')
                elif edit_type == '5':
                    print("Current note is {}: "
                          "go ahead and make your edit".format(result.notes))
                    new_entry_list = make_new_entry(
                        task_date=result.date, task_job=result.job, task_minutes=result.time
                    )
                    delete_entry(result)
                    result.notes = new_entry_list[3]
                    add_entry(new_entry_list)
                    print('Entry has been updated')
            elif action == 'N':
                clear_tscreen()
                continue
            elif action == 'B':
                exit_string_search = False
                break
            elif action == 'X':
                input("Are you sure? press any key to permanently delete this entry > ")
                delete_entry(result)
                results.remove(result)
                print('Entry deleted successfully')
                if len(results) == 0:
                    exit_string_search = False
                    print('No results left to look at')
                else:
                    continue


def clear_tscreen():
    if 'Windows' in platform.architecture()[1]:
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':

    clear_tscreen()

    if filename not in os.listdir(dir_path):
        file_create = open(file_path, 'w')
        file_create.close()

    while True:
        action_selection = input("What do you want to do quit ('Q'),  make an entry ('A')\n "
                                 "Get total number of entries ('G'), print all entries('P')\n "
                                 "or search the log ('S') > ").upper().strip()
        if action_selection == 'Q':
            break
        elif action_selection == 'A':
            clear_tscreen()
            add_entry(make_new_entry())
            print("Added task to log successfully!")
        elif action_selection == 'S':
            while True:
                clear_tscreen()
                search_method = input("Do you want to search by date ('D'), time spent ('T')\n "
                                        "words ('W'), or pattern ('P')\n "
                                        "or go back to the previous menu ('R') > ").upper().strip()
                if search_method == 'D':
                    while True:
                        ds_method = input("Do you want to search by a specific date ('1')\n A range of dates ('2') or"
                                          " see a list of dates with entries to choose from ('3')\n or go back ('4')? ")
                        if ds_method == '1':
                            while True:
                                date_lookup = validate_date(input(" Enter search date as 'dd/mm/yyyy > "))
                                if date_lookup:
                                    break
                            ds_search_results = date_search(specific_date=date_lookup)
                            if ds_search_results:
                                big_function(ds_search_results)
                            else:
                                print("Searching for {} generated zero results".format(date_lookup))
                                break
                        elif ds_method == '2':
                            while True:
                                begin_date = validate_date(input("Enter start of date range as 'dd/mm/yyyy > "))
                                end_date = validate_date(input("Enter end of date range as 'dd/mm/yyyy > "))
                                if begin_date and end_date:
                                    start_and_end_dates = begin_date, end_date
                                    dr_search_results = date_search(range_of_dates=start_and_end_dates)
                                    if dr_search_results is not None:
                                        break
                                    else:
                                        print("The Start date must be earlier than the End date\n And both must be"
                                              "entered in the correct format")
                            if dr_search_results:
                                big_function(dr_search_results)
                            else:
                                print("searching between {} and {} generated zero results".format(begin_date, end_date))
                        elif ds_method == '4':
                            break
                        elif ds_method == '3':
                            entry_list_for_search = build_search_list()
                            list_of_dated_entries = [(idx + 1, obj.date) for idx, obj in enumerate(entry_list_for_search)]
                            for thing in list_of_dated_entries:
                                print("index {}: date {}".format(thing[0], thing[1]))
                            while True:
                                try:
                                    index_ref = int(input("For the date you want to see entries for\n "
                                                  "please enter the index number > "))
                                    break
                                except ValueError:
                                    print("please enter a number for the index you wish to search")
                            viewing_list = []
                            for id_date in list_of_dated_entries:
                                if id_date[0] == index_ref:
                                    for entryobj in entry_list_for_search:
                                        if entryobj.date == id_date[1]:
                                            viewing_list.append(entryobj)
                            big_function(viewing_list)
                elif search_method == 'W':
                    clear_tscreen()
                    string_lookup = input('Enter the words you want to search for separated by a space > ')
                    w_search_results = string_search(string_lookup)
                    if w_search_results:
                        big_function(w_search_results)
                    else:
                        print("searching for {} generated zero results".format(string_lookup))
                elif search_method == 'T':
                    clear_tscreen()
                    while True:
                        print("You need to enter a base time in minutes\n then a range in minutes to search around the"
                              "base time\n a range of zero will search for entries with the exact base"
                              " time spent on the task ")
                        time_lookup = validate_time_spent(input("Enter first the base time > "))
                        time_range = validate_time_spent(input("Enter the range time > "))
                        if time_lookup and time_range:
                            break
                    t_search_results = time_search(time_lookup, time_range)
                    if t_search_results:
                        big_function(t_search_results)
                    else:
                        print("Searching for tasks taking {} minutes plus\nand minus {} minutes "
                              "produced no results".format(time_lookup, time_range))
                elif search_method == 'P':
                    clear_tscreen()
                    print("You will need to enter a regular expression to match\n"
                          "against the entries job and notes fields, entries will be formatted into raw strings\n"
                          "if not done explicitly, you should also omit the quote marks")
                    regular_expression = input("Please enter a valid regular expression to search with > ")
                    p_search_results = expression_search(regular_expression)
                    if p_search_results:
                        big_function(p_search_results)
                    else:
                        print("Searching with the regular expression '{}' produced no results".format(regular_expression))
                elif search_method == 'R':
                    break
        elif action_selection == 'P':
            for entry_to_print in build_search_list():
                print('\n')
                print_search_result(entry_to_print)
        elif action_selection == 'G':
            print('\nThere are {} entries in total'.format(len(build_search_list())))
