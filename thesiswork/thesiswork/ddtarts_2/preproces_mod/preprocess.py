import csv
import codecs
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import sys
import os.path
import string
csv.field_size_limit(2**16)
maxInt = sys.maxsize
import ast
from textblob import TextBlob

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
nltk.download('stopwords')

nltk.download('brown')
nltk.download('averaged_perceptron_tagger')
class Preprocess:
    def __init__(self,readpath,writepath):
        self.readpath = readpath
        self.writepath = writepath
        self.content = []
        self.original = []
        self.sort_content = dict()
        self.reverse_stem_model = dict()
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "../resource/tags.txt")
        file = codecs.open(path, 'r', 'utf-8')
        self.tags = []
        for corr in file:
            for word in corr.split():
                self.tags.append(word)
    @staticmethod
    def textFile(readpath):
        line_data = []
        with open(readpath) as file_in:
            for line in file_in:
                line_data.append(line.strip())
        return line_data

    def readStemmingModel(self):
        self.readCsv()
        for stem_row in self.content:
            self.reverse_stem_model[stem_row[0]] = stem_row[1]
        return self.reverse_stem_model

    def process(self):
        count =0
        print("Total commits: " + str(len(self.content)))
        for row in self.content:
            # if(self.checkSpecial(row[1])):
            #     continue
            msg = self.clean(row[1])
            #print(msg)

            termlist = msg.split()

            termlist2 = [str.rstrip(x.lower(), ',.?!') for x in termlist]
            words = self.removeSTopword(termlist2)
            if(len(words)>2):
                #self.content.remove(row)
                #print(words)
                count = count+1
                self.sort_content[row[0]] = len(words)
        print("Total more than: " + str(count))

    def cleanContent(self):
        count = 0
        print("Total commits: " + str(len(self.content)))
        for row in self.content:
            # if(self.checkSpecial(row[1])):
            #     continue
            msg = self.clean(row[1])
            # print(msg)

            termlist = msg.split()

            termlist2 = [str.rstrip(x.lower(), ',.?!') for x in termlist]
            words = self.wordStemming(self.removeSTopword(termlist2))
            self.content[count][1] = words
            count = count+1
    def skipStopsForAll(self, content_index):
        for row in self.content:
            row[content_index] = self.removeSTopword(row[content_index])

    def cleanForAll(self, content_index):

        for row in self.content:
            cleaned = set()
            for word in row[content_index]:
                word = word.lower().replace(".", "").replace(":","").replace(",","").replace("'","")
                if(word=="" or word==" " or word=="a" or word=="if" or word =="the" or word =="is" or word=="or" or word=="it"):
                    continue
                cleaned.add(word)
            row[content_index] = list(cleaned)

    def stemmingSamples(self, content_indx = 6):
        count = 0
        for row in self.content:

            termlist = self.cleanCodeElement(row[content_indx])

            termlist2 = row[2].split()
            words = self.wordStemming(termlist)
            words2 = self.wordStemming(termlist2)
            self.content[count][content_indx] = words
            self.content[count][1] = words2
            count = count + 1
    #here cat_indx is message index and content_indx is the concept words
    #TODO- this method is problematic in case when handling category index and content index. Must be changed
    def stemmingCleanSamples(self, cat_indx=1,content_indx = 6):
        count = 0
        for row in self.content:

            termlist = row[content_indx].split() #self.skipSTopword(row[content_indx].split())#row[content_indx].split() # for annotated conecpt words

            termlist2 = self.wordsWithCodeToken(row[cat_indx].split()) #self.skipSTopword(row[cat_indx].split()) #row[cat_indx].split() #self.wordsWithCodeToken(row[cat_indx].split()) # for commit message words # Three options: t_w, t_s, t_p
            words = self.wordStemming(termlist)
            words2 = self.wordStemming(termlist2)
            self.content[count][content_indx] = words
            self.content[count][cat_indx] = words2
            count = count + 1

    def correctStemmingWithCode(self, content_indx = 2, retain_index=5):
        count = 0
        for row in self.content:

            self.content[count][retain_index] =row[content_indx]
            termlist = self.wordsWithCodeToken(row[content_indx].split()) #self.skipSTopword(row[cat_indx].split()) #row[cat_indx].split() #self.wordsWithCodeToken(row[cat_indx].split()) # for commit message words # Three options: t_w, t_s, t_p
            words = self.wordStemming(termlist)
            self.content[count][content_indx] = words
            count = count + 1

    def newTokenStemming(self, content_indx = 2):
        count = 0
        for row in self.content:
            text_words = []

            text_words = row[content_indx].replace(' ', '').split(',')
            print(text_words)
            words = self.wordStemming(text_words)
            self.content[count][content_indx] = words
            count = count + 1

    def wordsWithCodeToken(self, words):
        extended_words = []
        for word in words:
            for token in self.codeToToekn(word):
                extended_words.append(token)
        return extended_words

    def codeToToekn(self, name):
        return re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split()
    def wordStemming(self, example_words):
        ps = PorterStemmer()

        words = []
        for w in example_words:
            wd = str(w)
            words.append(ps.stem(wd))
        return words
    def findCodeElement(self, text):
        match1 = re.findall(r'[\S]+\.[\S]+', text)
        match2 = re.findall(r'([\w]+[A-Z]+[\S]*)', text)
        if(len(match1)>0 or len(match2)>0 ):
            if(len(match1)>0):
                print(match1)
            if (len(match2)>0):
                print(match2)
            return text
        return None

    def cleanCodeElement(self, text):
        for extra_term in CLEAN_TERMS:
            text = text.split(extra_term)[0]
        text = re.sub(r'[\S]+\.[\S]+','', text)
        text = re.sub(r'([\w]+[A-Z]+[\S]*)', '',text)
        text = re.sub(r'[\w]+\/+[\w]+[\/+[\S]+]?','', text) #kv/query/views hadoop-yarn-server-web-proxy ejb->jpa asd() asd(asd)

        text = re.sub(r'[\w]+\-+[\w]+[\-+[\S]+]?', '',text)

        text = re.sub(r'[\w]+\->+[\w]+[\->+[\S]+]?','', text)

        text = re.sub(r'[\w]+\([\S]*\)','', text)
        text = re.sub(r'\([\S \s]*\)', '', text)
        text = text.replace("\n", " ")
        text = text.replace(".", "")
        text = text.replace("Motivation ----------", "")
        text = text.replace("Changes -------", "")
        text = text.replace("Motivation: -----------", "")
        return text

    def clean(self, text):
        for extra_term in CLEAN_TERMS:
            text = text.split(extra_term)[0]

        text = text.replace("\n"," ")

        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
        text = text.replace(".","")
        return text

    def checkSpecial(self, txt):


        for sw in SP_WORDS:
            if sw in txt:
                return True
        if any(txt in s for s in self.tags):
            print("found")
            return True
        return False
    def removeSpecialWord(self, word_list):
        filtered_word_list = word_list[:]
        for word in word_list:
            if(self.checkSpecial(word)):
                filtered_word_list.remove(word)
        return filtered_word_list

    def removeSTopword(self, word_list):
        filtered_word_list = word_list[:]  # make a copy of the word_list
        for word in word_list:  # iterate over word_list

         if(word is ""):
            filtered_word_list.remove(word)
         elif (word in "Bug"):
             filtered_word_list.remove(word)
         elif (word in "bug"):
             filtered_word_list.remove(word)
         elif(word.isalpha() is False):
             filtered_word_list.remove(word)
         elif any(word in s for s in self.tags):
             filtered_word_list.remove(word)

        # if(len(filtered_word_list)<3):
        #     return ["single"]
        for word in word_list:  # iterate over word_list

         if word in stopwords.words('english'):
            if(word in filtered_word_list):
                filtered_word_list.remove(word)
        return filtered_word_list

    def skipSTopword(self, word_list):
        filtered_word_list = word_list[:]  # make a copy of the word_list
        for word in word_list:  # iterate over word_list

         if word in stopwords.words('english'):
            if(word in filtered_word_list):
                filtered_word_list.remove(word)
        return filtered_word_list

    def wordstemming(self):
        pass
    def readCsv(self):
        csvfile = open(self.readpath, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            self.original.append(row)
            self.content.append(row)

        csvfile.close()

    def readCsvByColumnExtension(self):
        csvfile = open(self.readpath, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        EL = [None] * 4
        for row in reader:
            self.original.append(row)
            self.content.append([row[0], "", row[2], "", "", "", ""])

        csvfile.close()

    # def contentColumnExtension(self):

    def libraryNameEncoding(self, text_index, libname):
        indx=0
        for content in self.content:
            api_encoded = content[text_index]
            for name in libname:
                api_encoded = api_encoded.replace(name, "aaa")
            self.content[indx][text_index] = api_encoded
            indx=indx+1
    def writeClean(self, cat_indx=3, test_indx=5):
        print("Total commits: " + str(len(self.content)))
        count = 0
        fl = open(self.writepath, 'w')
        csv_write = csv.writer(fl)
        for row in self.content:
            if (row[cat_indx].lower() not in ["adaptive", "corrective", "perfective", "preventive"]):
                continue
            msg = self.clean(row[1])
            # print(msg)
            termlist = self.removeSpecialWord(msg.split())

            termlist2 = [str.rstrip(x.lower(), ',.?!') for x in termlist]
            #words = self.removeSTopword(termlist2)
            if (len(termlist2) > 1):
                count = count + 1
                csv_write.writerow([row[0], ' '.join(termlist2), row[2], row[3], row[4], row[5]])
        print("Filtered: " + str(count))
        fl.close()
    def writeWithCode(self, cat_indx=3, test_indx=5):
        print("Total commits: " + str(len(self.content)))
        count = 0
        fl = open(self.writepath, 'w')
        csv_write = csv.writer(fl)
        for row in self.content:
            if (row[cat_indx].lower() not in ["adaptive", "corrective", "perfective", "preventive"]):
                continue
            msg = self.cleanCodeElement(row[1])

            if (msg != None):
                count = count + 1
                csv_write.writerow([row[0], msg, row[2], row[3], row[4], row[5]])
        print("Filtered: " + str(count))
        fl.close()

    def writeCSV(self):
        print("Total commits: " + str(len(self.content)))
        count =0
        fl = open(self.writepath, 'w')
        csv_write = csv.writer(fl)
        for row in self.content:
            msg = self.clean(row[1])
            # print(msg)
            termlist = msg.split()

            termlist2 = [str.rstrip(x.lower(), ',.?!-+') for x in termlist]
            words = self.removeSTopword(termlist2)
            if (len(words) > 1):
                count = count +1
                csv_write.writerow([row[0], row[1], row[2], row[3]])
        print("Filtered: " + str(count))
        fl.close()

    def writeTopSort(self):
        print("Total commits: " + str(len(self.content)))
        count =0
        fl = open(self.writepath, 'w')
        csv_write = csv.writer(fl)
        listofTuples = sorted(self.sort_content.items(), key=lambda x: len(x[0]),reverse=True)
        allkeys = []
        for elem in listofTuples[:1000]:
            allkeys.append(elem[0])
        #allkeys = top.keys()
        for row in self.content:
            if (row[0] in allkeys):
                count = count +1
                csv_write.writerow([row[0], row[1], row[2], row[3]])
        print("Filtered: " + str(count))
        fl.close()

    def findToken(self, dest_list, seach_tok):
        for d_token in dest_list:
            if seach_tok == d_token:
                return True
        else:
            return False

    def preparedOp(self, text_indx=2,op_index=1):
        for i in range(len(self.content)):
            row = self.content[i]
            ops = row[op_index]
            if(ops=="NON_M2M" or ops==" " or ops==''):
                print(ops)
                continue
            t_list = ops.split(',')
            discard_list = set()
            for txt in t_list:
                if(self.findToken(["CLASS_ADD", "MO_NEW"],txt)==True):
                    discard_list.add("ONLY_ADD")
                elif(self.findToken(["CLASS_DELETE", "DELETE_MO"],txt)==True):
                    discard_list.add("ONLY_DELETE")
                elif(self.findToken(["MODIFY_CONNECT", "MODIFY_CONNECT_API"],txt)==True):
                    discard_list.add("MODIFY_CONNECT")
                elif(self.findToken(["MODIFY_DISCONNECT", "MODIFY_DISCONNECT_API"],txt)==True):
                    discard_list.add("MODIFY_DISCONNECT")
                else:
                    discard_list.add(txt)
            row[op_index] = ((',').join(list(discard_list)))
            self.content[i]=row


    def separateOnlyTitle(self, text_indx=2,op_index=1):
        purified = []
        for i in range(len(self.content)):
            row = self.content[i]
            ops = row[op_index]
            if(ops=="NON_M2M" or ops==" " or ops==''):
                print(ops)
                continue
            text = row[text_indx]
            modified = []
            modified_final = []
            t_list = text.split('\n')
            discard_list = []
            for txt in t_list:
                if((txt.lstrip(' ').find('-', 0) == 0) or (txt.lstrip(' ').find("*", 0)==0)):
                    discard_list.append(txt)
                else:
                    modified.append(txt)
            if(len(discard_list)==len(t_list)):
                modified = t_list
            for m_text in modified:
                if(m_text==' '):
                    pass
                else:
                    modified_final.append(m_text)
            row.append((' ').join(modified_final))
            purified.append(row)
        self.content=purified

    @staticmethod
    def onlyTitle(text):
        modified = []
        modified_final = []
        t_list = text.split('\n')
        discard_list = []
        for txt in t_list:
            if((txt.lstrip(' ').find('-', 0) == 0) or (txt.lstrip(' ').find("*", 0)==0)):
                discard_list.append(txt)
            else:
                modified.append(txt)
        if(len(discard_list)==len(t_list)):
            modified = t_list
        for m_text in modified:
            if(m_text==' '):
                pass
            else:
                modified_final.append(m_text)

        return (' ').join(modified_final[:2])
    @staticmethod
    def nounPhrase(text):
        # txt = """Natural language processing (NLP) is a field of computer science, artificial intelligence, and computational linguistics concerned with the inter
        # % actions between computers and human (natural) languages."""
        blob = TextBlob(text)
        # print(blob.noun_phrases)

        token_map = {}
        words = []
        nount = []
        adjectivet = []
        for tag in blob.tags:
            tok, pos = tag

            if (pos == "NN"):
                nount.append(tok)
            if ("JJ" in pos):
                res = re.findall("[^ a-zA-Z]+", tok)
                if (len(res) == 0):
                    adjectivet.append(tok)
                else:
                    pass

        nount = sorted(nount, key=len, reverse=True)
        adjectivet = sorted(adjectivet, key=len, reverse=True)
        for line in blob.noun_phrases:
            line = line.strip()
            words_in_line = line.split(" ")
            token_map[line] = (len(words_in_line), line)

        noun_phrase_list = sorted(token_map.values(), reverse=True)
        noun_lists = []
        for n_p in noun_phrase_list:
            ind, val = n_p
            noun_lists.append(val)
        # if(len(noun_lists)<1):
        #     noun_lists = nount
        if(len(nount)<1):
            nount.append("")
        if(len(adjectivet)<1):
            adjectivet.append("")
        return (noun_lists, nount, adjectivet)
    @staticmethod
    def filterAlphaWords(noun_lists):

        if(len(noun_lists)>1):
            filtered_list = []
            for text in noun_lists:
                res = re.findall("[^ a-zA-Z]+", text)
                if(len(res)==0):
                    filtered_list.append(text)
            if(len(filtered_list)>0):
                return filtered_list[0]
            else:
                return noun_lists[0]

        elif(len(noun_lists)==1):
            return noun_lists[0]
        else:
            print("Noun lists----------------------->>>>>>>>>>>>>>>>>", noun_lists)
            return noun_lists

    @staticmethod
    def specialWord(text):
        t_list = text.split('\n')
        special_words = ["deprecate", "sq", "sonarqube", "smell", "readable", "simpl", "annotat"]
        wording = ""
        for line in t_list:
            words_in_line = line.split(" ")
            for word in words_in_line:
                for keyw in special_words:
                    if keyw in word.lower():
                        wording = "for " + word.lower()
                        break
        return wording
# wordsFreqDict = {
#     "hello": 56,
#     "at" : 23 ,
#     "test" : 43,
#     "this" : 43
#     }
# top = list(wordsFreqDict.keys())[:2]
#
# for ky in top:
#     print(ky)
#
# sys.exit(1)
# preprocs = Preprocess("/mnt/hadoop/vlab/archiword/jvm_commits.csv","/mnt/hadoop/vlab/archiword/jvm_1k.csv")
# preprocs.readCsv()
# preprocs.process()
# #preprocs.writeCSV()
# preprocs.writeTopSort()
#
#
# print("test preproces_mod")

class DataSave:
    def __init__(self,writepath,content):
        self.writepath = writepath
        self.content = content #expect a list of samples TODO - content could be various datatypes
    def plainSaveCSV(self):
        fl = open(self.writepath, 'w')
        csv_write = csv.writer(fl)
        for row in self.content:
            csv_write.writerow(row)
        fl.close()
    #TODO-this method only saves having single type change
    def doubleSaveCSV(self, another_path,cat_indx = 3):
        temp_content = []
        fl2 = open(another_path, 'w')
        csv_write2 = csv.writer(fl2)
        for row in self.content:
            if(',' in row[cat_indx]):
                pass
            else:
                csv_write2.writerow(row)
                temp_content.append(row)
        fl2.close()
        return temp_content
    #TODO-this method only saves having multiple types change
    def onlyMultipleTypesSave(self, cat_indx = 3):
        temp_content = []
        fl2 = open(self.writepath, 'w')
        csv_write2 = csv.writer(fl2)
        for row in self.content:

            if (',' in row[cat_indx]):
                csv_write2.writerow(row)
                temp_content.append(row)
        print("Tangled commits:" ,len(temp_content))
        fl2.close()
        return temp_content

    def saveAsText(self, change_obj,dir):
        change_obj.savefoldFile(dir)

    def saveLinesToFile(self, filename,content):
        file = open(filename + ".txt", "w")
        file.writelines(content)
        file.close()

    def saveSSCWordMap(self, filename):
        file = open(filename + ".txt", "w")
        i = 0
        ssc_keys = self.content.keys()
        for ssc_key in ssc_keys:
            words = self.content.get(ssc_key)
            sorted_prev = sorted(words.items(), key=lambda kv: kv[1], reverse=True)
            formatted_word = ""
            for wordp in sorted_prev:
               formatted_word = formatted_word+ " "+wordp[0] +":" +str(wordp[1])
            file.write(ssc_key +"-->" + formatted_word+ '\n')

            i += 1
        file.close()

    def plainTextSave(self, filename, content):
        file = open(filename + ".txt", "w")
        file.write(content)
        file.close()
    def readSSCWordMap(self, filename):
        ssc_list = []
        with open(filename+".txt") as f:
            lines = [line for line in f]
            for line in lines:
                ssc_list.append(line)

        return ssc_list
