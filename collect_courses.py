import re
import urllib.request
import json
from bs4 import BeautifulSoup


# a brief description of how this script works:

# there are course catalog for ICS and CS courses

# we're going to scrape both the ICS and CS courses for any and all courses that either are prerequisites for a course,
# or are courses that requires one or more prerequisites

class collectCourse:  # this class has a method that returns a dictionary with (key, value) pairs
                        #  being a prerequisite and a list of courses that the prerequisite maps to

    def __init__(self):
        self.course_dictionary = dict()  # dictionary that will be returned, containing the class mapping

    def get_dictionary(self, url):  # this is the method that's invoked to return the dictionary

        pat = re.compile(r'(I&C\s+SCI\s+\d+\w*)|(IN4MATX\s+\d+\w*)|(COMPSCI\s+\d+\w*)|(MATH\s+\d+\w*)|(STATS\s+\d+\w*)|'
                         r'(NET\s+SYS\s+\d+\w*)')
        # this is a regex pattern that will match all of the instances of *****almost***** any prerequisite course
        # this regular expression will also work on either the ICS (lower div) or CS (upper div) page
        # we need further work to extend this to to match ~~~any and all~~~ courses
        # example: BIO, CHEM, AFAM, ANTHRO etc

        thepage = urllib.request.urlopen(url)  # opens the url passed through the method

        soup = BeautifulSoup(thepage, "html.parser")  # creates a beautiful soup object that will allow for parsing

        classes_with_prereqs = []  # this list will hold all of the classes that have prerequisites
        for link in soup.select("div .courseblock"):  # iterates entire page - looks for divs with the class courseblock
            if "Prerequisite" in link.text:  # if the div tag contains the phrase "prerequisite" anywhere in its text
                classes_with_prereqs.append(link.text)  # add it to the list of classes that contain prerequisites

        # prereqs now contains all of the classes that have prerequisites

        prereq_course = []  # this list will contain tuples in the following format
        # (prerequisite, course)

        for text in classes_with_prereqs:
            course = text.partition('.')[0]  # gets the title of the class that has a prerequisite
            # Explanation:
            # the course title will be something like this:
            # "\nI&C SCI 6B. Boolean Algebra and Logic. 4 Units"
            # We only want the "I&C SCI 6B" part, because that's what we'll put on the node

            # here's how we get it
            # Every course is delimited by a period

            # text.partition(".") partitions text into 3 different parts
            # partition[0] is "\nI&C SCI 6B"
            # partition[1] is "."
            # partition[2] is Boolean Algebra and Logic. 4 Units"
            # we are only concerned with the partition[0], which is why course = partition(".")[0]

            course = course[1:len(course)]  # removes the newline character, "\n", at the beginning of the string
            # course is now a key to the dictionary

            prereq = text.partition("Prerequisite")[2]
            # text.partition("Prerequisite") returns a 3 tuple
            # text.partition("Prerequisite")[0] returns the text ~before~ the phrase "Prequisite", which is a lot
            # text.partition("Prerequisite")[1] returns the actual phrase "Prerequisite"
            # text.partition("Prerequisite")[2] returns the text ~after~ the phrase "Prerequisite"

            # we're interersted in text.partition("Prerequisite")[2] because it lists out the prerequisites for a course

            # text.partition("Prerequisite")[2] returns something along the lines of:
            # """CSE 21 or I&C SCI 21 or I&C SCI H21. CSE 21 with a grade of C or better.
            # I&C SCI 21 with a grade of C or better. I&C SCI H21 with a grade of C or better.
            # Same as CSE 22. Overlaps with I&C SCI H22, CSE 42, I&C SCI 32, CSE 43, I&C SCI 33. (II, Vb)"""

            # this is a long string of text, and its important to note that
            # the required courses are always the first sentence in text.partition("Prerequisite")[2]

            # You can think of it as the prerequisites are delimited by a "." character, and we are only interested in
            # the first delimited phrase

            prereq = prereq.partition('.')[0]
            # this takes the giant string of text that was returned from text.partition("Prerequisite")[2]
            # and gets the first sentence from that string of text, something like "CSE 21 or I&C SCI 21 or I&C SCI H21"
            # which is a string that contains all of the prerequisite courses that we are interested in

            """IT'S EXTREMELY IMPORTANT TO NOTE THAT THERE ARE "AND" & "OR" KEYWORDS!!!
                We have to figure out how to interpret those words
            """

            prereq = re.findall(pat, prereq)
            # re.findall(pat, str) returns a tuple of matches for a particular regular expression
            # it's arguments are re.findall(regex_pattern_to_match, string_to_scan)
            # we're using the regex that we compiled at the top of this method and the prereq string we parsed above

            # prereq contains matches in the form of
            # ('I&C\xa0SCI\xa031', '', '', '', '', '')
            # ('I&C\xa0SCI\xa032', '', 'I&C\xa0SCI\xa051', '', '', '')
            # ('', '', 'I&C\xa0SCI\xa046', '', 'I&C\xa0SCI\xa0161')
            # there are empty strings in the tuple, we might need to fix this later, but maybe not, since it works

            for p in prereq:  # iterates over the list of regex matches, like ('I&C\xa0SCI\xa031', '', '', '', '', '')
                for word in p:
                    if word != "":  # this makes sure to get the actual prereq, not the empty strings that also matched
                        prereq_course.append((word, course))  # add the prereq and course mapping tuple to prereq_course

            # prereq_course is a list that now contains 2-tuples in this format
            # [...("ICS 31", "ICS 32"), ("ICS 31", "ICS 51")...]

        # this for loop will create the dictionary that will be returned by the method
        for p_c in prereq_course:  # p_c is an element of the list of 2-tuples described immediately above
            # p_c[0] is the prereq, ("ICS 31", ...)
            # p_c[1] is the course p_c[0] maps to (..., "ICS 32")
            if p_c[0] in self.course_dictionary.keys():  # if the prereq is already in the dict
                temp = [p_c[1]]
                self.course_dictionary[p_c[0]].extend(temp)  # this means there's already a list, so extend it
            else:  # if the prereq isn't already a key in the dictionary,
                self.course_dictionary.update({p_c[0]: [p_c[1]]})  # create a list of courses the preq maps to

        # self.course_dictionary now contains courses and prereqs in the form of
        # { "prerequisite": ["course 1", "course 2", "course 3"] }

        # something to note is that the dictionary will never contain an empty list

        return self.course_dictionary


if __name__ == "__main__":
    print("LOWER DIVISION DICT\n")
    course_obj_one = collectCourse()  # we have to create a new object every time we want to scrape a page
    # this is because every object will have a unique dictionary that will contain prerequisites and courses

    ics_dict = course_obj_one.get_dictionary("http://catalogue.uci.edu/allcourses/i_c_sci/")
    # ics_dict now has a mapping of all of any prerequisites and the courses it maps to for the ics page

    for p_c in sorted(ics_dict.items()):
        print(p_c[0], "goes to", p_c[1])
    print('\n\n\n\n\n\n\n\n\n\n\n\n')
    # this just prints out the prerequisite-course mappings

    print("UPPER DIVISION DICT\n")
    course_obj_two = collectCourse()
    cs_dict = course_obj_two.get_dictionary("http://catalogue.uci.edu/allcourses/compsci/")
    for pre_co in sorted(cs_dict.items()):
        print(pre_co[0], "goes to", pre_co[1])
    print('\n\n\n\n\n\n\n\n\n\n\n\n')

    # the for-loop is a bit weird and esoteric
    total_dict = dict()  # we want this dict to hold all of the prerequisites that map to any course
    for key1 in ics_dict.keys():  # iterate over the lower div dict
        for key2 in cs_dict.keys():  # iterate over the upper div dict
            if key1 == key2:  # if the keys are the same
                list_one = ics_dict[key1]
                list_two = cs_dict[key2]
                list_one.extend(list_two)  # then combine both lists into one
                final_list = list_one
                total_dict.update({key1: list(set(final_list))})  # update the dictionary
            else:  # if the keys aren't the same
                if key1 not in total_dict.keys():  # if key isn't in the dictionary
                    total_dict.update({key1: ics_dict[key1]})  # add it
                elif key2 not in total_dict.keys():  # if key isn't in the dictionary
                    total_dict.update({key2: cs_dict[key2]})  # add it

    # total_dict now contains all of the prerequisites-course mappings for lower and upper div computer science courses

    print("LOWER AND DIVISION DICTIONARY")
    for p_c in sorted(total_dict.items()):
        print(p_c[0], "maps to", end=" ")
        for i in sorted(p_c[1]):
            if len(p_c[1]) == 1 and i == p_c[1][-1]:
                print(i, end=".")
            elif i == sorted(p_c[1])[-1]:
                print("and "+ i, end=".")
            else:
                print(i, end=", ")
        print()
    # this for loop prints out the lower and upper prerequisites dictionary in a readable format

    # the code that follows relies on the sample schedule that was retrieved from the sample schedule on the catalogue
    # this code below ~will~ have to be modified if we want to extend this to majors outside of Donald Bren, which we do

    with open("C:\\users\\redsh\\downloads\\ICS_table_revised_V2.json") as file:
        data = json.load(file)
    # path leads to a file that contains a JSON file that contains a sample schedule for computer science
    # data now holds a json object

    classes_in_sample_schedule = []
    # this list will contain all of the classes that are found in the sample schedule

    for keys in data.keys():
        for dicts in data[keys]:  # takes the brackets away from the vals, even if the list consists of a single element
            for k in dicts.keys():
                classes_in_sample_schedule.append(dicts[k])
    # this for-loop is also very esoteric and has very peculiar details that have to do with the json sample schedule,
    # but we're eventually going to do a cross reference with another table of data, so don't worry too much about it

    class_graph_nodes = []  # this will hold all of the classes present in both the total_dict and the sample_schedule

    """!!!!!!!!!!!!!!!!!!!!!!!!this is barring specializations!!!!!!!!!!!!!!!!!!!!!!!!"""

    for pre_co in total_dict.items():  # iterates over the giant dictionary of lower and upper division courses
        first = pre_co[0].replace(u'\xa0', ' ')  # retrieves the prerequisite in the dictionary and changes the
        # character encoding to ensure keys work
        # the raw data scraped from the web has the character "\xa0",
        # this is ~~technically~~ not equivalent to the " " char

        if first in classes_in_sample_schedule:  # if the prerequisite is in the sample schedule
            class_graph_nodes.append(first)  # then add that to the list of classes that'll be used to render the graph
        for course in pre_co[1]:  # iterate over the list of courses the prerequisite maps to
            second = course.replace(u'\xa0', ' ')  # again, handle the character encoding to ensure keys and shit work
            if second in classes_in_sample_schedule:  # if any element is in the sample schedule
                class_graph_nodes.append(second)  # add that to the list of classes that'll be used to render the graph

    class_graph_nodes = sorted(set(class_graph_nodes))  # removes any duplicates added to the graph
    # we just want one instance of each class, which is why we do this

    print('\n\n\n\n\n\n\n\n\n\n\n\n')
    print("COURSE MAPPINGS")
    print('\n\n\n')

    for classes in class_graph_nodes:  # iterates over the list of course nodes
        key = classes.replace(u' ', u'\xa0')  # again, this deals with character encodings
        print(key, "maps to")
        for c in sorted(total_dict[key]):  # iterate over the list the prerequisite maps to
            if c.replace(u'\xa0', ' ') in class_graph_nodes:
                print(c, end=", ")
        print()
        print("**********")

    # figure out how to get Math 2A to map to Math 2B
        # scrape the javascript text that pops up when a link is clicked in

    # 6B -> 6D -> 161
    # this should be the chaining that is used to render the graph
    # However, since 6B is ~~technically~~ an explicit prerequisite to 161, where it should be an implicit prerequisite

    """
        corequisites should be displayed as a single node, with a note letting the user know that they're corequisites
        figure out how to do a chaining
    """
