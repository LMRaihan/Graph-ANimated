import csv
import codecs
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import sys
import string
csv.field_size_limit(2**16)
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)
caps = "([A-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
SP_WORDS = ["HDFS-","YARN-","HDDS-","HADOOP-", "MAPREDUCE-", "simonstewart:", "#","JVMCBC-","JCBC-","Motivation", "test" ,"bug", "hhh", "@", "Bug","Test", "------------","----------"]
CLEAN_TERMS = ["Change-Id:", "Signed-off-by:", "Reviewed-on:", "Reviewed-by:", "IP-Clean:", "Tested-by:", "git-svn-id", "This reverts commit", "Contributed by", "Conflicts:", "Modification", "Result"]
#nltk.download('stopwords')
DELETE = "DELETE"
RENAME = "RENAME"
ADD="ADD"
IMPORT_ADD ="import_add"
IMPORT_DELETE ="import_delete"
FUNCTION_ADD = "function_add"
FUNCTION_DELETE = "function_delete"
class Model:
    def __init__(self,readpath):
        self.readpath = readpath
        self.weight = {}
    def readModel(self):
        csvfile = open(self.readpath, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:

            self.weight[row[0]] = [row[1], row[2], row[3], row[4]]
        csvfile.close()

    # rule: (file ^ import) delete + no other addition ==> preventive
    # (file add ^ import add) + function add ==> perfective
    # (file + import) delete + (file ^ import) add ==> adaptive
    # import delete + (file ^ import) add ==> corrective
    @staticmethod
    def codePredictionRule( op_list=[]):
        is_file_delete = False
        is_file_add = False
        is_import_add = False
        is_import_delete = False
        is_function_delete = False
        is_function_add = False
        if(RENAME in op_list):
            op_list.remove(RENAME)
        if(FUNCTION_DELETE in op_list):
            is_function_delete = True
            op_list.remove(FUNCTION_DELETE)
        if(FUNCTION_ADD in op_list):
            is_function_add = True
            op_list.remove(FUNCTION_ADD)
        if(DELETE in op_list):
            is_file_delete = True
            op_list.remove(DELETE)
        if(not op_list):
            return 1 #preventive
        if(IMPORT_DELETE in op_list):
            is_import_delete =True
            op_list.remove(IMPORT_DELETE)
        if (not op_list):
            return 1  # still preventive
        if(IMPORT_ADD in op_list):
            is_import_add = True
            op_list.remove(IMPORT_ADD)
        if(not op_list):
            if(is_file_delete and is_import_delete):
                return 3 # adaptive
            if(is_import_delete):
                return 2 # corrective
            if(is_function_add):
                return 0 # perfective

        if(ADD in op_list):
            is_file_add = True
            if(is_file_delete==False and is_import_delete==False):

                if (is_function_add):
                    return 0  # perfective
            if (is_file_delete and is_import_delete):
                return 3  # adaptive
            if (is_import_delete):
                return 2  # corrective

        return 0
