import csv
import operator
import collections
import os
import ast
from ChangeAnnotation.testing import Testing
from preproces_mod.preprocess import DataSave,Preprocess
class ChangedCommit():
    def __init__(self):
        self.project_name = "project"
        self.samples = []

class Change:
    classes = ["perfective", "preventive", "corrective", "adaptive"]
    MODULE_SUMMARY_INDEX = 5
    DESIGN_SUMMARY_INDEX = 6
    PREDICTED_WORDS_INDEX = 7
    def __init__(self, type):
        self.type = type
        self.word_p = {} #probaility of each word calculated from frequency # it could be operation types as well --> add, delete, rename, import_add, import_del, function_add, function_delete
        self.samples = [] # simply all words with duplicacy
        self.classes_impacted = set()
        self.total = 0
        self.reverse_stem_model = dict()
        self.noun_phrases = []
        self.nouns = []
        self.adjectives = []
    def putHash(self,word):
        if(word=='NON_M2M'):
            return
        self.samples.append(word)
        if word not in self.word_p.keys():
            self.word_p[word] = 1
        else:
            self.word_p[word] += 1
    def setOperation(self, ops):
        for op in ops:
            self.putHash(op)

    def setImpactedClasses(self, impacted):
        for cls in impacted:
            self.classes_impacted.add(cls)
    def setTotal(self, tot):
        self.total += tot
    def getKeys(self):
        return sorted(self.word_p.keys())
    def getValue(self, word):
        if(word in self.word_p.keys()):
            return self.word_p[word]
        else:
            return 0
    def normalize(self):
        for word in self.word_p:
            self.word_p[word] = round(self.word_p[word]/self.total,2)
    def print(self):
        print("------------------" + self.type+"-----------------")
        print(len(list(self.word_p.keys())))
        sorted_prev = sorted(self.word_p.items(), key=lambda kv: kv[1], reverse=True)
        for wordp in sorted_prev:
            print('(',wordp[0], ",", wordp[1],')')

    def save(self, csvfl):

        sorted_prev = sorted(self.word_p.items(), key=lambda kv: kv[1], reverse=True)
        for wordp in sorted_prev:
            csvfl.writerow([wordp[0], wordp[1]])
    def saveInText(self):
        os.mkdir(self.type)
        i= 0
        for sample in self.samples:
            file = open(self.type+"/"+str(i)+".txt", "w")
            file.write(sample[1])
            file.close()
            i+=1
    def saveInFile(self, dir,text_indx=1):
        file = open(dir + self.type + ".txt", "a")
        i= 0
        for sample in self.samples:

            file.write(sample[text_indx].replace('\n', ' ') + '\n')

            i+=1
        file.close()
    def savefoldFile(self, dir):
        try:
            dd = os.mkdir(dir)
        except:
            pass
        file = open(dir+"/" + self.type + ".txt", "a")
        i= 0
        for sample in self.samples:
            if(sample[1] is None or sample[1] ==''):
                continue
            file.write(sample[1].replace('NON_M2M', '').replace("CLASS_ADD","").replace("MODIFY_API_CONNECT","").replace(',', ' ').replace('\n', ' ') + '\n')

            i+=1
        file.close()

    def saveConceptFile(self, dir, indx=6):
        try:
            dd = os.mkdir(dir)
        except:
            pass
        import ast
        file = open(dir + "/" + self.type + ".txt", "a")
        i = 0
        for sample in self.samples:
            if (sample[indx] is None or sample[indx] == ''):
                continue
            # ops= []
            # try:
            #     ops= ast.literal_eval(sample[indx])
            # except:
            #     print(sample[indx])
            #     ops = sample[indx].replace('[','').replace("'",'').replace(']','').split(',')
            file.write(" ".join(sample[indx]) +" " +sample[1].replace(",", " ").replace("NON_M2M","")+'\n')
            # file.write(sample[indx] + '\n')
            # file.write(" ".join(sample[indx])+'\n')
            i += 1
        file.close()
    def saveTextAndSCO(self, dir, text_indx=2, op_indx=1):
        try:
            dd = os.mkdir(dir)
        except:
            pass
        file = open(dir+"/" + self.type + ".txt", "a")
        i= 0
        for sample in self.samples:
            txt = sample[text_indx].replace('\n', ' ')
            file.write( txt) # + ' ' + sample[op_indx].replace(',', ' ').replace('NON_M2M','') + '\n')

            i+=1
        file.close()
    def saveTextAndOPForWeka(self,dir, text_indx=2, op_indx=1):
        os.mkdir(dir+"/" +self.type)
        i= 0
        for sample in self.samples:
            file = open(dir+"/" +self.type+"/"+str(i)+".txt", "w")
            txt = sample[text_indx].replace('\n', ' ')
            file.write(txt + ' ' + sample[op_indx].replace(',', ' '))
            file.close()
            i+=1
    def saveOPForWeka(self,dir, op_indx=1):
        os.mkdir(dir+"/" +self.type)
        i= 0
        for sample in self.samples:
            file = open(dir+"/" +self.type+"/"+str(i)+".txt", "w")
            file.write(sample[op_indx].replace(',', ' '))
            file.close()
            i+=1

class ModuleChange(Change):
    def __init__(self, type):
        super().__init__(type)
        self.module_operation={}
        self.module_del_operation = {}
        self.jpms = dict()
        self.classes=dict()
        self.ssc_token_map = dict()
        self.performance_scores = []
        self.rule_list = []
        self.rule_strings = []
    def putOperationHash(self,word, val):

        if word not in self.module_operation.keys():
            self.module_operation[word] = val
        else:
            self.module_operation[word] += val

    def components(self, mod_summary, d_summary):
        summary = ''
        mods = ''
        any_conn = False
        any_disconn = False
        ops_name = []
        mod_wize_summary = mod_summary[0]
        moved_cls_sumary = mod_summary[1]
        moved_method_summary = mod_summary[2]
        if(len(moved_cls_sumary)>0):
            ops_name.append(moved_cls_sumary[0] + " "+ moved_cls_sumary[1])
        if (len(moved_method_summary) > 0):
            ops_name.append(moved_method_summary[0] + " "+ moved_method_summary[1])

        for ky in mod_wize_summary.keys():
            mod_list, cls_list, mthd_list, has_non, has_conn, has_disconn, added, deleted, modified= mod_wize_summary[ky]
            any_conn = has_conn
            any_disconn = has_disconn
            single_content = ky
            ads = list(added)
            dels = list(deleted)
            modifies = list(modified)
            involved_classes = ""

            if (len(ads) > 0):
                involved_classes = involved_classes + "added:" + ",".join(ads)
                ops_name.append(",".join(ads)+ " added ")
            if (len(dels) > 0):
                involved_classes = involved_classes + "and deleted:" + ",".join(dels)
                ops_name.append(",".join(dels)+ " deleted ")
                any_disconn = True
            if (len(modifies)):
                involved_classes = involved_classes + "and modified:" + ",".join(modifies)
                ops_name.append(" class modified ")
            single_content = single_content + "||>" + involved_classes + "||>" + ",".join(list(mod_list))
            if (len(list(cls_list)) > 0):
                single_content = single_content + "<| class: " + ",".join(list(cls_list))
            if (len(list(mthd_list)) > 0):
                single_content = single_content + "<| method:" + ",".join(list(mthd_list))
                ops_name.append(",".join(list(mthd_list)) + " methods deleted or added ")
            summary = single_content + ";" + summary
            ops_name.append(" in " + ky +" module ")
            mods = ky + "," + mods
        if(len(moved_cls_sumary)>0):
            any_disconn = True
        if (len(moved_method_summary) > 0):
            any_disconn = True
        # print("---",str(any_disconn))
        return (mods, summary, any_conn, any_disconn, ops_name)

    def msgPartExtraction(self, processed_commit,msg_indx):
        plain_message = ""
        n_phrases, nouns, adjectives = Preprocess.nounPhrase(Preprocess.onlyTitle(processed_commit[msg_indx]))
        self.adjectives.extend(adjectives)
        self.nouns.extend(nouns)
        try:

            self.noun_phrases.append(",".join(n_phrases))
            if(len(n_phrases)>0):
                plain_message = " for " + adjectives[0] + " "+Preprocess.filterAlphaWords(n_phrases) + ";"
            else:
                plain_message = " for " + adjectives[0] + " "+nouns[0] + ";"
                print("Noun adjects---", nouns, adjectives)
        except Exception as e:
            print("problem----->", n_phrases, nouns, adjectives)
            print(e)
        return plain_message

    def generateContentForCommit(self, processed_commit, msg_indx, op_index):
        mods, summary, has_conn, has_disconn, ops_name = self.components(processed_commit[Change.MODULE_SUMMARY_INDEX], None)
        plain_message =""
        #TODO- message format ==> commit msg title parts + keywords + preposition + modified modules + sscs + code components change relations
        # if (has_conn):
        #     plain_message = Preprocess.onlyTitle(processed_commit[4]) + ";" + \
        #                     processed_commit[msg_index] + " in " + mods + " <=>" + processed_commit[
        #                         op_index].lower() + " <=>" + summary
        #TODO - sentence rule should be  ==> keywords + change operation + preposition + component + prepostion + Noun phrase
        # if(has_conn):
        # n_phrases =  Preprocess.nounPhrase(Preprocess.onlyTitle(processed_commit[msg_indx]))
        # self.noun_phrases.append(",".join(n_phrases))
        plain_message = " by " + " ".join(ops_name)+";" + "\n Change Relations:" + processed_commit[
                                op_index].lower() + "\n Deatils: " + summary
        return (has_conn,has_disconn, plain_message)

    def generatePerfectiveSentence(self, processed_commit, msg_index, op_index):
        mods, summary, has_conn, has_disconn, ops_name = self.components(processed_commit[Change.MODULE_SUMMARY_INDEX], None)
        plain_message =""
        #TODO- message format ==> commit msg title parts + keywords + preposition + modified modules + sscs + code components change relations
        # if (has_conn):
        #     plain_message = Preprocess.onlyTitle(processed_commit[4]) + ";" + \
        #                     processed_commit[msg_index] + " in " + mods + " <=>" + processed_commit[
        #                         op_index].lower() + " <=>" + summary
        #TODO - sentence rule should be  ==> keywords + change operation + preposition + component + prepostion + Noun phrase
        try:
            if(has_conn):
                n_phrases,nouns, adjectives =  Preprocess.nounPhrase(Preprocess.onlyTitle(processed_commit[msg_index]))
                self.noun_phrases.append(",".join(n_phrases))
                commit_theme =""
                if (len(n_phrases) > 0):
                    commit_theme = " for " + adjectives[0] + " " + Preprocess.filterAlphaWords(n_phrases) + ";"
                else:
                    commit_theme = " for " + adjectives[0] + " " + nouns[0] + ";"
                plain_message = processed_commit[Change.PREDICTED_WORDS_INDEX] + " by " + " ".join(ops_name) + commit_theme #+ "<=>" + processed_commit[op_index].lower() + " <=>" + summary
        except:
            print("problemitc opsname", ops_name)

        return (has_conn, plain_message)
    def generateCorrectiveSentence(self, processed_commit, msg_index, op_index):
        mods, summary, has_conn, has_disconn, ops_name = self.components(processed_commit[Change.MODULE_SUMMARY_INDEX], None)
        plain_message =""
        #TODO- message format ==> commit msg title parts + keywords + preposition + modified modules + sscs + code components change relations
        #TODO - sentence rule should be  ==> keywords + problem+ preposition + component
        n_phrases, nouns, adjectives = Preprocess.nounPhrase(Preprocess.onlyTitle(processed_commit[msg_index]))
        self.noun_phrases.append(",".join(n_phrases))
        commit_theme = ""
        try:
            if (len(n_phrases) > 0):
                commit_theme =  adjectives[0] + " " + Preprocess.filterAlphaWords(n_phrases)
            else:
                commit_theme =  adjectives[0] + " " + nouns[0]

            key_words = sorted(processed_commit[Change.PREDICTED_WORDS_INDEX].split(" ")[:3], key = len, reverse = True)
            plain_message = " ".join(key_words) +  " bug in " + commit_theme + " by " + " ".join(ops_name) +";"
        except:
            print("problemitc opsname", ops_name)

        #+ "<=>" + processed_commit[ op_index].lower() + " <=>" + summary
        return (0, plain_message)

    def generatePreventiveSentence(self, processed_commit, msg_index, op_index):
        mods, summary, has_conn, has_disconn, ops_name = self.components(processed_commit[Change.MODULE_SUMMARY_INDEX], None)
        plain_message =""
        #TODO- message format ==> commit msg title parts + keywords + preposition + modified modules + sscs + code components change relations
        #TODO - sentence rule should be  ==> keywords + change operation + preposition + component + prepostion + special word
        try:
            if(has_disconn):
                n_phrases, nouns, adjectives = Preprocess.nounPhrase(Preprocess.onlyTitle(processed_commit[msg_index]))

                commit_theme = ""
                commit_theme = " for " + adjectives[0] + " " + nouns[0]+";"
                key_words = sorted(processed_commit[Change.PREDICTED_WORDS_INDEX].split(" "), key=len, reverse=True)
                plain_message = " ".join(key_words[:3]) +  " by " +" ".join(ops_name) + Preprocess.specialWord(processed_commit[msg_index]) +commit_theme
                #+ "<=>" + processed_commit[op_index].lower() + " <=>" + summary
        except:
            print("problemitc opsname", ops_name)

        return (has_disconn, plain_message)

    def generateAdaptiveSentence(self, processed_commit, msg_index, op_index):
        mods, summary, has_conn, has_disconn, ops_name = self.components(processed_commit[Change.MODULE_SUMMARY_INDEX], None)
        plain_message =""
        #TODO- message format ==> commit msg title parts + keywords + preposition + modified modules + sscs + code components change relations
        #TODO - sentence rule should be  ==> keywords + preposition + adaptive element + preposition + component + prepostion + noun phrase
        n_phrases, nouns, adjectives = Preprocess.nounPhrase(Preprocess.onlyTitle(processed_commit[msg_index]))
        self.noun_phrases.append(",".join(n_phrases))
        try:
            commit_theme = ""
            if (len(n_phrases) > 0):
                commit_theme = " for " + adjectives[0] + " " + Preprocess.filterAlphaWords(n_phrases)
            else:
                commit_theme = " for " + adjectives[0] + " " + nouns[0]

            plain_message = processed_commit[Change.PREDICTED_WORDS_INDEX] +  " API/library/platform " +  " by " +" ".join(ops_name) + commit_theme
        except:
            print("problemitc opsname", ops_name)

        #+ "<=>" + processed_commit[op_index].lower() + " <=>" + summary
        return (0,plain_message)


    def parseSSCWords(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        ssc_list = DataSave("", "").readSSCWordMap(os.path.join(my_path,"../resource/sscwordmap_"+ self.type))
        for ssc_tok in ssc_list:
            ssc_parts = ssc_tok.split("--> ")
            self.populatesscWordHash(ssc_parts[0], ssc_parts[1])

    def parseRules(self):

        ssc_list = DataSave("", "").readSSCWordMap("rule_"+ self.type)
        for ssc_tok in ssc_list:
            ssc_parts = ast.literal_eval(ssc_tok)
            self.rule_list.append(ssc_parts)

    def transformRuleToStr(self):
        for rule in self.rule_list:
            self.rule_strings.append(" ".join(sorted(rule)))


    def populatesscWordHash(self, ssc, words):
        tokn_value = dict()
        wrd_part = words.split(" ")
        for wrd in wrd_part:
            if(wrd==" "):
                continue
            parts = wrd.split(":")
            tokn_value[parts[0]] = parts[1]
        self.ssc_token_map[ssc] = tokn_value

    def reverse_stemMsg(self,msg):
        message = set()

        for token in list(msg):
            if(token in self.reverse_stem_model.keys()):
                message.add(self.reverse_stem_model[token])
        return message
    def designMessage(self, op_index=1):

        for sample in self.samples:
            op = sample[op_index]
            sscs = op.split(',')
            message = set()
            for ssc in sscs:
                try:
                    ssc = ssc.strip(" ")
                    words = list(self.ssc_token_map.get(ssc).keys())
                    try:
                        words.remove("add")
                    except:
                        pass
                    try:
                        words.remove("display")
                    except:
                        pass
                    for word in words[0:4]:
                        message.add(word)
                except:
                    print(ssc)
            sample.append(" ".join(self.reverse_stemMsg(message)))

    def getAllMsgAsDoc(self, index):
        ref_whole_doc = ""
        for sample in self.samples:
            ref_doc = " ".join(sample[index])
            # print(sample[index])
            ref_whole_doc = ref_whole_doc + " " + ref_doc
        # print(ref_whole_doc)
        return ref_whole_doc
    def conceptTokenStat(self, index, tokens):
        existed_tokens = {}
        total = 0
        print(tokens)
        for sample in self.samples:
            # print(sample)
            for token in sample[index]:
                if(token in tokens):

                    if(token in list(existed_tokens.keys())):
                        existed_tokens[token] = int(existed_tokens.get(token)) + 1
                    else: existed_tokens[token]  =1
                    total = total + 1
        print(str(len(list(existed_tokens.keys()))), str(total))
    def messagePerformance(self, reference_index, generated_index):
        rouge_test = Testing()
        for sample in self.samples:
            ref_doc = " ".join(sample[reference_index])
            sample_doc = sample[generated_index]
            rouge_score = rouge_test.rougeScore(ref_doc, sample_doc)
            print(sample_doc)
            print("+++++++++++++++++++")
            print(ref_doc)
            print("---------------------")
            self.performance_scores.append([rouge_score.precision, rouge_score.fmeasure])

    def logAsDocPerformance(self, ref_whole_doc, generated_index):
        rouge_test = Testing()
        generated_doc =""
        for sample in self.samples:
            sample_doc = sample[generated_index]
            generated_doc = generated_doc +" "+ sample_doc
        rouge_score = rouge_test.rougeScore(ref_whole_doc, generated_doc)
        # print(sample_doc)
        # print("+++++++++++++++++++")
        # print(ref_doc)
        print("---------------------")
        self.performance_scores.append([rouge_score.precision, rouge_score.fmeasure])



    def messageAsDocPerformance(self, reference_index, generated_index):
        rouge_test = Testing()
        ref_whole_doc = ""
        generated_doc =""
        for sample in self.samples:
            ref_doc = " ".join(sample[reference_index])
            ref_whole_doc = ref_whole_doc + " " +ref_doc
            sample_doc = sample[generated_index]
            generated_doc = generated_doc +" "+ sample_doc
        rouge_score = rouge_test.rougeScore(ref_whole_doc, generated_doc)
        # print(sample_doc)
        # print("+++++++++++++++++++")
        # print(ref_doc)
        print("---------------------")
        self.performance_scores.append([rouge_score.precision, rouge_score.fmeasure])

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
    def sscWordMapping(self, op_index=1, concept_indx=6):

        for sample in self.samples:
            op = sample[op_index]
            sscs = op.split(',')
            words = sample[concept_indx]
            for ssc in sscs:
                self.sscWordHash(ssc, words)
        DataSave("", self.ssc_token_map).saveSSCWordMap("sscwordmap_" +self.type)

    def putDelOperationHash(self,word, val):

        if word not in self.module_del_operation.keys():
            self.module_del_operation[word] = val
        else:
            self.module_del_operation[word] += val
    def normalizeOperation(self):
        for word in self.module_operation:
            self.module_operation[word] = round(self.module_operation[word]/self.total,2)
    def normalizeDelOperation(self):
        for word in self.module_del_operation:
            self.module_del_operation[word] = round(self.module_del_operation[word]/self.total,2)
    def getOpValue(self, word):
        if(word in self.module_operation.keys()):
            return self.module_operation[word]
        else:
            return 0

    def printOpDistribution(self):
        print("------------------module operation distribution-----------------")
        sorted_prev = sorted(self.module_operation.items(), key=lambda kv: kv[1], reverse=True)
        for wordp in sorted_prev:
            print(wordp[0], ": ", wordp[1])

    def printDelOpDistribution(self):
        print("------------------module operation distribution-----------------")
        sorted_prev = sorted(self.module_del_operation.items(), key=lambda kv: kv[1], reverse=True)
        for wordp in sorted_prev:
            print(wordp[0], ": ", wordp[1])

    def graphGenerate(self):
        import matplotlib.pyplot as plt
        plt.rcdefaults()
        import numpy as np
        import matplotlib.pyplot as plt

        objects = []


        performance = []
        fl = open(self.type + "_jpms.csv", 'w')
        csv_write = csv.writer(fl)

        for word in collections.OrderedDict(sorted(self.word_p.items(), key=operator.itemgetter(1),reverse=True)):
            objects.append(word)
            performance.append(self.word_p[word])
            #csv_write.writerow([word,self.word_p[word] ])
        for word in collections.OrderedDict(sorted(self.module_operation.items(), key=operator.itemgetter(1),reverse=True)):
            if("/" in word or "*" in word):
                None
            else:
                objects.append(word)
                performance.append(self.module_operation[word])
                csv_write.writerow([word, self.module_operation[word]])
        for word in collections.OrderedDict(sorted(self.module_del_operation.items(), key=operator.itemgetter(1),reverse=True)):
            if ("/" in word or "*" in word):
                None
            else:
                objects.append("D_" + word)
                performance.append(self.module_del_operation[word])
                csv_write.writerow(["D_" + word, self.module_del_operation[word]])
        fl.close()
        objects.append("scale")
        performance.append(10)
        y_pos = np.arange(len(objects))
        plt.bar(y_pos, performance, align='center', alpha=0.5)
        plt.xticks(y_pos, objects,fontsize=8, rotation=60)
        plt.ylabel('Distribution')
        plt.title(self.type+  " change")

        plt.show()

    def putJpms(self, jpm):
        if jpm not in self.jpms.keys():
            self.jpms[jpm] = 1
        else:
            self.jpms[jpm] += 1

    def putClasses(self, cls):
        if cls not in self.classes.keys():
            self.classes[cls] = 1
        else:
            self.classes[cls] += 1

    def getJpmsInfo(self):
        hotspot = []
        keys = self.jpms.keys()
        lngth = len(keys)
        for ky in keys:
            val = self.jpms.get(ky)
            if((val/self.total)>=0.10):
                hotspot.append(ky)
        return [lngth, len(hotspot)]

    def getClassesInfo(self):
        hotspot = []
        keys = self.classes.keys()
        lngth = len(keys)
        for ky in keys:
            val = self.classes.get(ky)
            if ((val / self.total) >= .10):
                hotspot.append(ky)
        return [lngth, len(hotspot)]

    def a2aGist(self):
        return [self.total, self.getJpmsInfo(), self.getClassesInfo()]
#
# test_data = ["add", "change", "add"]
#
# adaptive = Change("adaptive")
# for data in test_data:
#     adaptive.putHash(data)
#
# adaptive.setTotal(3)
# adaptive.normalize()
# adaptive.print()
