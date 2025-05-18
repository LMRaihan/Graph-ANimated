import os, sys
import csv
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from category_analysis.category_mod import Category
csv.field_size_limit(2**16)
maxInt = sys.maxsize
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

class TangleCategory(Category):
    def __init__(self, content, raw_content=""):
        super().__init__(content,raw_content)
        # This method predict a test sample using two trained models, token-based and semantic operations based
    def getClsIndices(self, cats):
        cat_indices = []
        for typ in cats:
            cat_indices.append(classes.index(typ))
        return cat_indices
    def combinedPredict(self, save_path="", text_indx=1, retain_index=2,cat_indx=4, op_indx=10, threshold=0.5):
        uniform_threshold = threshold
        print("length ", len(self.testsamples))
        keywords = self.words_weight.keys()
        opwords = self.operations_weight.keys()

        # fl = open(save_path, 'w')
        # csv_write = csv.writer(fl)
        no_token = 0
        correct_prediction = 0
        tangled = 0
        commit_index = 0
        for doc in self.content:
            s_words = set(doc[text_indx])
            sample_words = list(s_words)
            sample_ops = []
            print(doc[op_indx])
            if (doc[op_indx] != ""):
                ops = doc[op_indx].split(",")
                for word in ops:
                    if ("NON_M2M" in word):
                        continue
                    if(word in S_WORDS):
                        # print("Skipped SSC:-->", word)
                        continue
                    sample_ops.append(word)
            sum_token = []
            sum_op = []
            combined_avg_sum = []
            # cats = doc[cat_indx].lower().replace(' ','').split(',')
            # print(sample_words)
            # if ("perfective" in doc[cat_indx].lower()):
            #     # print(word)
            #     perfective_total += 1
            #     Category.perfective_total += 1
            #
            # if ("corrective" in doc[cat_indx].lower()):
            #     corrective_total += 1
            #     Category.corrective_total += 1
            # if ("adaptive" in cats):
            #     print(sample_words)
            #     Category.adaptive_total += 1
            # if ("preventive" in doc[cat_indx].lower()):
            #     preventive_total += 1
            #     Category.preventive_total += 1
            for i in range(4):
                sum_token.append(0)
                sum_op.append(0)
                combined_avg_sum.append(0)
            found_toks =[]
            for word in sample_words:
                if (word not in S_WORDS):
                    if (word in keywords):
                        found_toks.append(word)
                        wght = self.words_weight[word]
                        ind = 0
                        for wt in wght:
                            sum_token[ind] += float(wt)
                            ind += 1
            for word in Category.AAA:
                # print("testing ", word)
                if(self.apiNameMatching(word, doc[retain_index])==True):
                    word = 'aaa'
                    found_toks.append(word)
                    ind = 0
                    wght = self.words_weight[word]

                    for wt in wght:
                        sum_token[ind] += float(wt)
                        ind += 1

            for word in sample_ops:
                if (word not in S_WORDS):

                    if (word in opwords):
                        wght = self.operations_weight[word]
                        ind = 0
                        for wt in wght:
                            sum_op[ind] += float(wt)
                            ind += 1


            N = 2
            m = max(sum_token)
            top_index = 0
            indexes = [] # for V-w(ci)<= Threshold
            uniform_indexes = [] # for w(ci)/tot_sum >= Threshold
            if (m == 0):
                max_op = max(sum_op)
                top_index = sum_op.index(max(sum_op))
                no_token += 1
                for i in range(0, 4):
                    if((max_op-sum_op[i]) <=threshold):
                        indexes.append(i)
                tot = sum(sum_op)
                if (tot == 0):
                    top_index = 0
                    uniform_indexes.append(0)
                else:
                    for i in range(0, 4):
                        if((sum_op[i]/tot) >=uniform_threshold):
                            uniform_indexes.append(i)

            else:
                for i in range(0, 4):
                    combined_avg_sum[i] = round((sum_token[i] + sum_op[i]) / 2,
                                                2)  # + sum_op[i]/4#round((sum[i] + sum_op[i])/2,4)
                max_avg = max(combined_avg_sum)
                for i in range(0, 4):
                    if((max_avg-combined_avg_sum[i]) <=threshold):
                        indexes.append(i)
                tot = sum(combined_avg_sum)
                if(tot==0):
                    top_index=0
                    uniform_indexes.append(0)
                else:
                    for i in range(0, 4):
                        if ((combined_avg_sum[i] / tot) >= uniform_threshold):
                            uniform_indexes.append(i)
                    top_index = combined_avg_sum.index(max(combined_avg_sum))
            predicted_category = []
            print(uniform_indexes)
            for cat_indx in uniform_indexes:
                predicted_category.append(classes[int(cat_indx)])
            self.content[commit_index][3] =predicted_category
            commit_index +=1
            #
            # val = sum.index(max(sum))
            #
            #
            # if (m > 0):
            #     ms = [i for i, j in enumerate(sum) if j == m]
            #     if (len(ms) > 1):
            #         print(ms)
            #         ind_v = {}
            #         for ind in ms:
            #             w_d = {}
            #             for word in sample_words:
            #                 if (word in keywords):
            #                     wght = self.words_weight[word][ind]
            #                     w_d[word] = wght
            #             hm_v = max(w_d.items(), key=operator.itemgetter(1))
            #             ind_v[ind] = hm_v[1]
            #         val = max(ind_v.items(), key=operator.itemgetter(1))[0]

            # indexes = sorted(range(len(sum)), key=lambda sub: sum[sub])[-N:]
            # if(len(indexes)==len(cats)):
            #     correct_prediction +=1
            # if(len(indexes)>1):
            #     tangled +=1
            # if(len(uniform_indexes)==len(cats)):
            #     correct_prediction +=1
            #     cat_indices = self.getClsIndices(cats)
            #     uniform_indexes.sort()
            #     cat_indices.sort()
            #     for i in range(len(uniform_indexes)):
            #         self.ouctome(uniform_indexes[i], cat_indices[i])
            # if(len(uniform_indexes)>1):
            #     tangled +=1
            # csv_write.writerow(
            #     [doc[0], doc[1], doc[2], doc[3], classes[top_index], found_toks, sum_op, sum_token,uniform_indexes])

            # if (top_index == 0):
            #     # print(word)
            #     perfective_predic += 1
            #     Category.perfective_predic += 1
            #
            # if (top_index == 2):
            #     corrective_predic += 1
            #     Category.corrective_predic += 1
            # if (top_index == 3):
            #     adaptive_predic += 1
            #     Category.adaptive_predic += 1
            # if (top_index == 1):
            #     preventive_predic += 1
            #     Category.preventive_predic += 1
            # if ("perfective" in doc[cat_indx].lower() and top_index == 0):
            #     perfective_true += 1
            #     Category.perfective_true += 1
            # if ("corrective" in doc[cat_indx].lower() and top_index == 2):
            #     corrective_true += 1
            #     Category.corrective_true += 1
            # if ("adaptive" in doc[cat_indx].lower() and top_index == 3):
            #     adaptive_true += 1
            #     Category.adaptive_true += 1
            # if ("preventive" in doc[cat_indx].lower() and top_index == 1):
            #     preventive_true += 1
            #     Category.preventive_true += 1
        # fl.close()
        # perfect_false_positive = perfective_predic - perfective_true
        # perfect_false_negative = perfective_total - perfective_true
        # prevent_false_positive = preventive_predic - preventive_true
        # prevent_false_negative = preventive_total - preventive_true
        # adapt_false_positive = adaptive_predic - adaptive_true
        # adapt_false_negative = adaptive_total - adaptive_true
        # correct_false_positive = corrective_predic - corrective_true
        # correct_false_negative = corrective_total - corrective_true
        #
        # if (perfective_predic != 0):
        #     Category.FOLDpr += perfective_true / (perfective_true + perfect_false_negative)
        # if (preventive_predic != 0):
        #     Category.FOLDpvr += preventive_true / (preventive_true + prevent_false_negative)
        # if (corrective_predic != 0):
        #     Category.FOLDcr += corrective_true / (corrective_true + correct_false_negative)
        # if (adaptive_predic != 0):
        #     Category.FOLDar += adaptive_true / (adaptive_true + adapt_false_negative)
        #
        # Category.FOLDpp += perfective_true / (perfective_true + perfect_false_positive)
        # Category.FOLDpvp += preventive_true / (preventive_true + prevent_false_positive)
        # Category.FOLDcp += corrective_true / (corrective_true + correct_false_positive)
        # Category.FOLDapp += adaptive_true / (adaptive_true + adapt_false_positive)
        # Category.ALLp += (perfective_true + preventive_true + adaptive_true + corrective_true) / (
        #             perfective_true + perfect_false_positive + preventive_true + prevent_false_positive + corrective_true + correct_false_positive + adaptive_true + adapt_false_positive)
        # Category.ALLr += (perfective_true + preventive_true + adaptive_true + corrective_true) / (
        #             perfective_true + perfect_false_negative + preventive_true + prevent_false_negative + corrective_true + correct_false_negative + adaptive_true + adapt_false_negative)

        # This method predict a test sample using two trained models, token-based and association rules
