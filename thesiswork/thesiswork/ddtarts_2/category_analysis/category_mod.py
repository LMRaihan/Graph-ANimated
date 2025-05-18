import csv
import codecs
import nltk
from nltk.corpus import stopwords
import re
import sys
import string
import operator
import os, sys
import ast

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from category_analysis.change import *
from category_analysis import model
from postprocess.semanticop import *
from preproces_mod.preprocess import Preprocess,DataSave
csv.field_size_limit(2**16)
maxInt = sys.maxsize
PROJ = ["hadoop","hibernate","javaclient","jvm","linuxtools"]

classes = ["perfective", "preventive", "corrective","adaptive" ]
HEADER=["name","category", "requires","exports","module","provides","transitive","uses","open","with","D_requires","D_exports","D_module","D_provides","D_transitive","D_uses","D_open","D_with"]
while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)
S_WORDS = ["to","in","of","from", "CLASS_ADD", "MODIFY_API_CONNECT"]#,"function_delete", "function_add"]
EXCLUDE_WORDS = ["import","private","public","protected","package", "return"]
perfectiveO = ModuleChange("perfective")
adaptiveO = ModuleChange("adaptive")
preventiveO = ModuleChange("preventive")
correctiveO = ModuleChange("corrective")
allcategory = ModuleChange("All")
jpms_fl = open("operations_jpms.csv", 'w')
jpms_write = csv.writer(jpms_fl,quoting=csv.QUOTE_ALL)
jpms_write.writerow(HEADER)

discard = 0

class Category:
    predicted_samples = []
    FOLDpr = 0
    FOLDpvr = 0
    FOLDcr = 0
    FOLDar = 0
    BBB = set()
    AAA = set()
    FOLDpp = 0
    FOLDpvp = 0
    FOLDcp = 0
    FOLDapp = 0
    ALLp = 0
    ALLr = 0
    perfective_total = 0
    corrective_total = 0
    adaptive_total = 0
    preventive_total = 0
    perfective_predic = 0
    corrective_predic = 0
    adaptive_predic = 0
    preventive_predic = 0
    perfective_true = 0
    corrective_true = 0
    adaptive_true = 0
    preventive_true = 0
    perfect_false_positive = 0
    perfect_false_negative = 0
    prevent_false_positive = 0
    prevent_false_negative = 0
    correct_false_positive = 0
    correct_false_negative = 0
    adapt_false_positive = 0
    adapt_false_negative = 0
    connect_SCO=['CLASS_ADD', 'MO_NEW','MO_CONNECT', 'MODIFY_CONNECT','MODIFY_NEW_METHOD','MODIFY_CONNECT_API', 'MODIFY_NEW_API_METHOD']
    disconnect_SCO = ['CLASS_DELETE','DELETE_MO','MO_DISCONNECT','MODIFY_DISCONNECT','MODIFY_DELETE_METHOD','MODIFY_DISCONNECT_API','MODIFY_DELETE_API_METHOD']
    @staticmethod
    def resetMetric():
        Category.predicted_samples = []
        Category.FOLDpr = 0
        Category.FOLDpvr = 0
        Category.FOLDcr = 0
        Category.FOLDar = 0
        Category.BBB = set()
        Category.AAA = set()
        Category.FOLDpp = 0
        Category.FOLDpvp = 0
        Category.FOLDcp = 0
        Category.FOLDapp = 0
        Category.ALLp = 0
        Category.ALLr = 0
        Category.perfective_total = 0
        Category.corrective_total = 0
        Category.adaptive_total = 0
        Category.preventive_total = 0
        Category.perfective_predic = 0
        Category.corrective_predic = 0
        Category.adaptive_predic = 0
        Category.preventive_predic = 0
        Category.perfective_true = 0
        Category.corrective_true = 0
        Category.adaptive_true = 0
        Category.preventive_true = 0
        Category.perfect_false_positive = 0
        Category.perfect_false_negative = 0
        Category.prevent_false_positive = 0
        Category.prevent_false_negative = 0
        Category.correct_false_positive = 0
        Category.correct_false_negative = 0
        Category.adapt_false_positive = 0
        Category.adapt_false_negative = 0
    def __init__(self, content, raw_content=""):
        self.original = raw_content
        self.content = content
        self.perfective_content = []
        self.preventive_content = []
        self.adaptive_content = []
        self.corrective_content = []
        self.words_weight = {}
        self.operations_weight = {}
        self.testsamples = []
        self.perfective = ModuleChange("perfective")
        self.adaptive = ModuleChange("adaptive")
        self.preventive = ModuleChange("preventive")
        self.corrective = ModuleChange("corrective")
        self.ssc_token_map = dict()

    def resetForFolding(self):
        self.words_weight = {}
        self.operations_weight = {}
        self.perfective = ModuleChange("perfective")
        self.adaptive = ModuleChange("adaptive")
        self.preventive = ModuleChange("preventive")
        self.corrective = ModuleChange("corrective")
        self.testsamples = []

    def extendContent(self, contnt):
        self.content.extend(contnt)
    def extendTestSamples(self, contnt):
        self.testsamples.extend(contnt)

    def sscWordHash(self, ssc, words):
        for wrd in words:
            t_keys = self.ssc_token_map.keys()
            tokn_value = dict()
            if (ssc in t_keys):
                tokn_value = self.ssc_token_map.get(ssc)
            word_keys = tokn_value.keys()
            if (wrd in word_keys):
                wrd_value = tokn_value.get(wrd)
                tokn_value[wrd] = wrd_value + 1
            else:
                tokn_value[wrd] = 1
            self.ssc_token_map[ssc] = tokn_value

    def populatesscWordHash(self, ssc, words):
        tokn_value = dict()
        wrd_part = words.split(" ")
        for wrd in wrd_part:
            if(wrd==" "):
                continue
            parts = wrd.split(":")
            tokn_value[parts[0]] = parts[1]
        self.ssc_token_map[ssc] = tokn_value

    def writePValue(self, csv_w, key, contain, denometor, cat):
        if (denometor > 0):
            csv_w.writerow([key, (contain[key] / denometor), cat])

    def apiNameListing(self, cat_indx=4):

        testt = 0
        # generate the word2id and id2word maps and count the number of times of words showing up in documents
        for document in self.content:

            if (document[cat_indx].lower() not in ["adaptive", "corrective", "perfective", "preventive"] ):
                testt +=1
                continue

            # print(segList)
            # segList = jieba.cut(document)


            if ("adaptive" in document[cat_indx].lower()):
                for word in document[6]:
                    if(word == 'bbb'):
                        #print("init", document[7])
                        for trm in document[7].replace("/", ",").split(","):
                            Category.BBB.add(trm.lower())
                    elif(word == 'aaa'):
                        #print("init ", document[7])
                        for trm in document[7].replace("/", ",").split(","):
                            Category.AAA.add(trm.lower())

        print("discarded ", testt)
    def printApis(self):
        for ap in list(Category.BBB):
            print(ap)
        for ap in list(Category.AAA):
            print(ap)
    def libraryNameListing(self, cat_indx=3, lib_index=4):

        testt = 0
        # generate the word2id and id2word maps and count the number of times of words showing up in documents
        for document in self.content:

            # print(segList)
            # segList = jieba.cut(document)
            # print(document[5])

            if ("adaptive" in document[cat_indx].lower()):
                for word in document[lib_index]:
                    for trm in word.replace("/", ",").split(","):
                            Category.BBB.add(trm.lower())

    def libraryList(self, lib_name):
        print(lib_name)
        for word in lib_name:
            Category.AAA.add(word.lower())

    def separateCat(self, cat_indx=4):

        testt = 0
        # generate the word2id and id2word maps and count the number of times of words showing up in documents
        for document in self.content:

            # if (document[cat_indx].lower() not in ["adaptive", "corrective", "perfective", "preventive"] ):
            #     testt +=1
            #     continue
            # if(document[6] is None or document[6]=="" or len(document[6])<1):
            #     testt += 1
            #     continue
            # print(segList)
            # segList = jieba.cut(document)
            # print(document[5])
            change_type = document[cat_indx].lower().replace(" ","").split(",")[0]
            if ("perfective" in change_type):
                # print(word)
                self.perfective_content.append(document)

            if ("corrective" in change_type):
                self.corrective_content.append(document)
            if ("adaptive" in change_type):
                self.adaptive_content.append(document)
            if ("preventive" in change_type):
                self.preventive_content.append(document)
        print("Perfective:", str(len(self.perfective_content)))
        print("preventive:", str(len(self.preventive_content)))
        print("corrective:", str(len(self.corrective_content)))
        print("adaptive:", str(len(self.adaptive_content)))
        print("discarded ", testt)

    def separatePredictCat(self, cat_indx=4):

        testt = 0
        # generate the word2id and id2word maps and count the number of times of words showing up in documents
        for document in self.content:

            # if (document[cat_indx].lower() not in ["adaptive", "corrective", "perfective", "preventive"] ):
            #     testt +=1
            #     continue
            # if(document[6] is None or document[6]=="" or len(document[6])<1):
            #     testt += 1
            #     continue
            # print(segList)
            # segList = jieba.cut(document)
            # print(document[5])
            change_type = document[cat_indx]
            if ("perfective" in change_type):
                # print(word)
                self.perfective_content.append(document)

            if ("corrective" in change_type):
                self.corrective_content.append(document)
            if ("adaptive" in change_type):
                self.adaptive_content.append(document)
            if ("preventive" in change_type):
                self.preventive_content.append(document)
        print("Perfective:", str(len(self.perfective_content)))
        print("preventive:", str(len(self.preventive_content)))
        print("corrective:", str(len(self.corrective_content)))
        print("adaptive:", str(len(self.adaptive_content)))
        print("discarded ", testt)

    def separateCatObjects(self):
        self.perfective.samples = self.perfective_content
        self.preventive.samples = self.preventive_content
        self.adaptive.samples = self.adaptive_content
        self.corrective.samples = self.corrective_content

    def allSamplesAsPerfective(self):
        self.perfective.samples = self.perfective_content
        self.perfective.samples.extend(self.preventive_content)
        self.perfective.samples.extend(self.adaptive_content)
        self.perfective.samples.extend(self.corrective_content)

    def trainSSCWordMap(self, op_index=1, concept_indx=6):
        self.perfective.sscWordMapping(op_index, concept_indx)
        self.preventive.sscWordMapping(op_index, concept_indx)
        self.adaptive.sscWordMapping(op_index, concept_indx)
        self.corrective.sscWordMapping(op_index, concept_indx)

    def loadTrainedSSCWordMap(self):
        self.perfective.parseSSCWords()
        self.preventive.parseSSCWords()
        self.adaptive.parseSSCWords()
        self.corrective.parseSSCWords()
    def reverseStemming(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        preprocs = Preprocess(os.path.join(my_path,"../resource/reverse_stem.csv"),"")
        reverse_stem_model = preprocs.readStemmingModel()
        self.perfective.reverse_stem_model = reverse_stem_model
        self.preventive.reverse_stem_model = reverse_stem_model
        self.adaptive.reverse_stem_model = reverse_stem_model
        self.corrective.reverse_stem_model = reverse_stem_model

    def designMessageGeneration(self, save_path, op_index):
        self.reverseStemming()
        self.perfective.designMessage(op_index)
        self.preventive.designMessage(op_index)
        self.adaptive.designMessage(op_index)
        self.corrective.designMessage(op_index)


        DataSave(save_path+"/latest_design_message.csv", self.perfective.samples + self.preventive.samples+self.corrective.samples+self.adaptive.samples).plainSaveCSV()

    def designMessagePerformance(self, ref_index, generate_index):
        self.perfective.messagePerformance(ref_index, generate_index)
        self.preventive.messagePerformance(ref_index, generate_index)
        self.adaptive.messagePerformance(ref_index, generate_index)
        self.corrective.messagePerformance(ref_index, generate_index)

    def designMessageAsDocPerformance(self, ref_index, generate_index):
        self.perfective.messageAsDocPerformance(ref_index, generate_index)
        self.preventive.messageAsDocPerformance(ref_index, generate_index)
        self.adaptive.messageAsDocPerformance(ref_index, generate_index)
        self.corrective.messageAsDocPerformance(ref_index, generate_index)

    def allTypeAsPerfectivePerformance(self, ref_index, generate_index):
        self.perfective.messageAsDocPerformance(ref_index, generate_index)

    def changeLogAsDocPerformance(self, cat_log, ref_index, generate_index):

        self.perfective.logAsDocPerformance(cat_log.perfective.getAllMsgAsDoc(ref_index), generate_index)
        self.preventive.logAsDocPerformance(cat_log.preventive.getAllMsgAsDoc(ref_index), generate_index)
        self.adaptive.logAsDocPerformance(cat_log.adaptive.getAllMsgAsDoc(ref_index), generate_index)
        self.corrective.logAsDocPerformance(cat_log.corrective.getAllMsgAsDoc(ref_index), generate_index)

    def allLogAsPerfectivePerformance(self, cat_log, ref_index, generate_index):

        self.perfective.logAsDocPerformance(cat_log.perfective.getAllMsgAsDoc(ref_index), generate_index)
    def collectScores(self):
        all_scores = self.perfective.performance_scores
        all_scores.extend(self.preventive.performance_scores)
        all_scores.extend(self.adaptive.performance_scores)
        all_scores.extend(self.corrective.performance_scores)
        histo = [0, 0, 0, 0, 0]
        for scores in all_scores:
            if(scores[0] < 0.20):
                histo[0] +=1
            if(scores[0] >=0.20 and scores[0]<0.40):
                histo[1] +=1
            if (scores[0] >= 0.40 and scores[0] < 0.60):
                histo[2] += 1
            if (scores[0] >= 0.60 and scores[0] < 0.80):
                histo[3] += 1
            if (scores[0] >= 0.80):
                histo[4] += 1


        print(histo)
        print(self.perfective.performance_scores)
        print(self.preventive.performance_scores)
        print(self.adaptive.performance_scores)
        print(self.corrective.performance_scores)

    def collectSingleTypeScores(self):
        print(self.perfective.performance_scores)

    def normalize(self):
        self.perfective.normalize()
        self.preventive.normalize()
        self.adaptive.normalize()
        self.corrective.normalize()
    def graphprint(self):
        for op_name in RuleName.getOpNameList():
            p_h =  self.perfective.word_p.get(op_name) if op_name in list(self.perfective.word_p.keys()) else 0
            pv_h = self.preventive.word_p.get(op_name) if op_name in list(self.preventive.word_p.keys()) else 0
            c_h =self.corrective.word_p.get(op_name) if op_name in list(self.corrective.word_p.keys()) else 0
            a_h =self.adaptive.word_p.get(op_name) if op_name in list(self.adaptive.word_p.keys()) else 0
            print(op_name, "&", p_h, "&",pv_h, "&",c_h, "&",a_h)
            # self.preventive.print()
            # self.adaptive.print()
            # self.corrective.print()
    def normalizeJoint(self):
        self.perfective.normalize()
        self.preventive.normalize()
        self.adaptive.normalize()
        self.corrective.normalize()
        self.perfective.normalizeOperation()
        self.preventive.normalizeOperation()
        self.adaptive.normalizeOperation()
        self.corrective.normalizeOperation()
    def trainJointModel(self, save_file='weight.csv'):

        for word in self.perfective.word_p:
            if(word not in self.words_weight.keys()):
                pvalue = self.perfective.getValue(word)
                prvalue = self.preventive.getValue(word)
                cvalue = self.corrective.getValue(word)
                avalue = self.adaptive.getValue(word)
                tv = pvalue+prvalue+avalue+cvalue
                if(tv!=0):
                    self.words_weight[word] = [(pvalue/tv), (prvalue/tv), (cvalue/tv), (avalue/tv)]

        for word in self.preventive.word_p:
            if(word not in self.words_weight.keys()):
                pvalue = self.perfective.getValue(word)
                prvalue = self.preventive.getValue(word)
                cvalue = self.corrective.getValue(word)
                avalue = self.adaptive.getValue(word)
                tv = pvalue+prvalue+avalue+cvalue
                if (tv != 0):
                    self.words_weight[word] = [(pvalue/tv), (prvalue/tv), (cvalue/tv), (avalue/tv)]
        for word in self.corrective.word_p:
            if(word not in self.words_weight.keys()):
                pvalue = self.perfective.getValue(word)
                prvalue = self.preventive.getValue(word)
                cvalue = self.corrective.getValue(word)
                avalue = self.adaptive.getValue(word)
                tv = pvalue+prvalue+avalue+cvalue
                if (tv != 0):
                    self.words_weight[word] = [(pvalue/tv), (prvalue/tv), (cvalue/tv), (avalue/tv)]
        for word in self.adaptive.word_p:
            if(word not in self.words_weight.keys()):
                pvalue = self.perfective.getValue(word)
                prvalue = self.preventive.getValue(word)
                cvalue = self.corrective.getValue(word)
                avalue = self.adaptive.getValue(word)
                tv = pvalue+prvalue+avalue+cvalue
                if (tv != 0):
                    self.words_weight[word] = [(pvalue/tv), (prvalue/tv), (cvalue/tv), (avalue/tv)]
        for word in self.perfective.module_operation:
            if(word not in self.operations_weight.keys()):
                pvalue = self.perfective.getOpValue(word)
                prvalue = self.preventive.getOpValue(word)
                cvalue = self.corrective.getOpValue(word)
                avalue = self.adaptive.getOpValue(word)
                tv = pvalue+prvalue+avalue+cvalue
                if(tv!=0):
                    self.operations_weight[word] = [(pvalue/tv), (prvalue/tv), (cvalue/tv), (avalue/tv)]

        for word in self.preventive.module_operation:
            if(word not in self.operations_weight.keys()):
                pvalue = self.perfective.getOpValue(word)
                prvalue = self.preventive.getOpValue(word)
                cvalue = self.corrective.getOpValue(word)
                avalue = self.adaptive.getOpValue(word)
                tv = pvalue+prvalue+avalue+cvalue
                if (tv != 0):
                    self.operations_weight[word] = [(pvalue/tv), (prvalue/tv), (cvalue/tv), (avalue/tv)]
        for word in self.corrective.module_operation:
            if(word not in self.operations_weight.keys()):
                pvalue = self.perfective.getOpValue(word)
                prvalue = self.preventive.getOpValue(word)
                cvalue = self.corrective.getOpValue(word)
                avalue = self.adaptive.getOpValue(word)
                tv = pvalue+prvalue+avalue+cvalue
                if (tv != 0):
                    self.operations_weight[word] = [(pvalue/tv), (prvalue/tv), (cvalue/tv), (avalue/tv)]
        for word in self.adaptive.module_operation:
            if(word not in self.operations_weight.keys()):
                pvalue = self.perfective.getOpValue(word)
                prvalue = self.preventive.getOpValue(word)
                cvalue = self.corrective.getOpValue(word)
                avalue = self.adaptive.getOpValue(word)
                tv = pvalue+prvalue+avalue+cvalue
                if (tv != 0):
                    self.operations_weight[word] = [(pvalue/tv), (prvalue/tv), (cvalue/tv), (avalue/tv)]


    def apiNameMatching(self,name, name_list):
        n_list = name_list.split(" ")
        for token in n_list:
            if(name in token.lower()):
                return True
        return  False
    def wordpurification(self, word):
        word = word.replace('?','')
        return word
    #This method predict a test sample using two trained models, token-based and semantic operations based
    def findConnectSCO(self, ops):
        for op in ops:
            if op in Category.connect_SCO:
                return True
        return False

    def finddisConnectSCO(self, ops):
        for op in ops:
            if op in Category.disconnect_SCO:
                return True
        return False

    def testPrepear(self, cat_indx=4, test_indx=5, content_indx=6):
        for document in self.content:
            if (document[cat_indx].lower() not in ["adaptive", "corrective", "perfective", "preventive"]):
                continue
            self.testsamples.append(document)
    def tangledTestPrepear(self, cat_indx=4, test_indx=5, content_indx=6):
        for document in self.content:
            self.testsamples.append(document)
    def changeOperationInCode(self, op_index=9, cat_indx=4):

        for sample in self.testsamples:
            if ("perfective" in sample[cat_indx].lower()):
                # print(word)
                self.perfective.total += 1

            if ("corrective" in sample[cat_indx].lower()):
                self.corrective.total += 1
            if ("adaptive" in sample[cat_indx].lower()):
                self.adaptive.total += 1
            if ("preventive" in sample[cat_indx].lower()):
                self.preventive.total += 1
            str = sample[op_index]
            text = re.sub(r'[\s]*\+[\s]*', '+', str)
            txts = text.split('+')
            print(txts)
            if ("perfective" in sample[cat_indx].lower()):
                # print(word)
                for word in txts:
                    self.perfective.putHash(word)

            if ("corrective" in sample[cat_indx].lower()):
                for word in txts:
                    self.corrective.putHash(word)

            if ("adaptive" in sample[cat_indx].lower()):
                for word in txts:
                    self.adaptive.putHash(word)

            if ("preventive" in sample[cat_indx].lower()):
                for word in txts:
                    self.preventive.putHash(word)
    def designIdsHash(self, op_index=9, cat_indx=4):

        for sample in self.content:
            if ("perfective" in sample[cat_indx].lower()):
                # print(word)
                self.perfective.total += 1

            if ("corrective" in sample[cat_indx].lower()):
                self.corrective.total += 1
            if ("adaptive" in sample[cat_indx].lower()):
                self.adaptive.total += 1
            if ("preventive" in sample[cat_indx].lower()):
                self.preventive.total += 1
            txt = sample[op_index]
            txts = txt.split(',')
            # for word in ops:
            #     self.storingOps(word, self.perfective)
            # print(txts)
            # if ("perfective" in sample[cat_indx].lower()):
                # print(word)
            for word in txts:
                self.perfective.putHash(word.strip())

            if ("corrective" in sample[cat_indx].lower()):
                for word in txts:
                    self.corrective.putHash(word)

            if ("adaptive" in sample[cat_indx].lower()):
                for word in txts:
                    self.adaptive.putHash(word)

            if ("preventive" in sample[cat_indx].lower()):
                for word in txts:
                    self.preventive.putHash(word)

    def sscWordMapping(self, op_index=1, concept_indx=6):

        for sample in self.content:
            op = sample[op_index]
            sscs = op.split(',')
            words = sample[concept_indx]
            for ssc in sscs:
                self.sscWordHash(ssc, words)
        DataSave("", self.ssc_token_map).saveSSCWordMap("sscwordmap")

    def designMessage(self, save_path, op_index=1):

        for sample in self.content:
            op = sample[op_index]
            sscs = op.split(',')
            message = set()
            for ssc in sscs:
                words = list(self.ssc_token_map.get(ssc).keys())
                for word in words[0:4]:
                    message.add(word)
            sample.append(" ".join(message))
        DataSave(save_path+"/experiment_design_message.csv", self.content).plainSaveCSV()

    def parseSSCWords(self, filename):
        ssc_list = DataSave("", "").readSSCWordMap("sscwordmap")
        for ssc_tok in ssc_list:
            ssc_parts = ssc_tok.split("--> ")
            self.populatesscWordHash(ssc_parts[0], ssc_parts[1])
        print(self.ssc_token_map)
        print(self.ssc_token_map.keys())

    def saveSemanticOpInotHash(self, op_index=9, cat_indx=4):

        for sample in self.content:
            if ("perfective" in sample[cat_indx].lower()):
                # print(word)
                self.perfective.total += 1

            if ("corrective" in sample[cat_indx].lower()):
                self.corrective.total += 1
            if ("adaptive" in sample[cat_indx].lower()):
                self.adaptive.total += 1
            if ("preventive" in sample[cat_indx].lower()):
                self.preventive.total += 1
            txt = sample[op_index]
            txts = txt.split(',')
            # for word in ops:
            #     self.storingOps(word, self.perfective)
            # print(txts)
            if ("perfective" in sample[cat_indx].lower()):
                # print(word)
                for word in txts:
                    self.perfective.putHash(word)

            if ("corrective" in sample[cat_indx].lower()):
                for word in txts:
                    self.corrective.putHash(word)

            if ("adaptive" in sample[cat_indx].lower()):
                for word in txts:
                    self.adaptive.putHash(word)

            if ("preventive" in sample[cat_indx].lower()):
                for word in txts:
                    self.preventive.putHash(word)


    def newTestPrepear(self, cat_indx=4, test_indx=5, content_indx=6):
        testt = 0
        # generate the word2id and id2word maps and count the number of times of words showing up in documents
        for document in self.content:
            if ("test" in document[test_indx].lower()):
                self.testsamples.append(document)
                print("Test found")
                testt += 1
                continue

    def assignModel(self, weights):
        self.words_weight = weights

    def assignOperationModel(self, weights):
        self.operations_weight = weights
    def createTextFiles(self, cat_indx=4):
        for doc in self.content:

            if (doc[6] is None or doc[6] == "" or len(doc[6]) < 1):

                continue
            #print(sample_words)
            if ("perfective" in doc[cat_indx].lower()):
                # print(word)
                perfectiveO.samples.append(doc)

            if ("corrective" in doc[cat_indx].lower()):
                correctiveO.samples.append(doc)
            if ("adaptive" in doc[cat_indx].lower()):
                adaptiveO.samples.append(doc)
            if ("preventive" in doc[cat_indx].lower()):
                preventiveO.samples.append(doc)
    def seprateForTextFiles(self, dir,cat_indx=3,text_indx=2):
        for doc in self.content:

            #print(sample_words)
            if ("perfective" in doc[cat_indx].lower()):
                # print(word)
                perfectiveO.samples.append(doc)

            if ("corrective" in doc[cat_indx].lower()):
                correctiveO.samples.append(doc)
            if ("adaptive" in doc[cat_indx].lower()):
                adaptiveO.samples.append(doc)
            if ("preventive" in doc[cat_indx].lower()):
                preventiveO.samples.append(doc)

        perfectiveO.saveInFile(dir, text_indx)
        preventiveO.saveInFile(dir, text_indx)
        adaptiveO.saveInFile(dir, text_indx)
        correctiveO.saveInFile(dir, text_indx)

    def foldedTestSamples(self, cat_indx=4):
        perfective_t = ModuleChange("perfective")
        corrective_t = ModuleChange("corrective")
        adaptive_t=ModuleChange("adaptive")
        preventive_t = ModuleChange("preventive")
        for doc in self.testsamples:

            if (doc[6] is None or doc[6] == "" or len(doc[6]) < 1):

                continue
            #print(sample_words)
            if ("perfective" in doc[cat_indx].lower()):
                # print(word)
                perfective_t.samples.append(doc)

            if ("corrective" in doc[cat_indx].lower()):
                corrective_t.samples.append(doc)
            if ("adaptive" in doc[cat_indx].lower()):
                adaptive_t.samples.append(doc)
            if ("preventive" in doc[cat_indx].lower()):
                preventive_t.samples.append(doc)
        return (perfective_t, preventive_t, adaptive_t, corrective_t)

