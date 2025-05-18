from numpy.random import randn
from numpy.random import seed
from numpy import mean
from numpy import var,std
from math import sqrt
import numpy as np
from scipy import stats
from rouge_score import rouge_scorer

class Testing:
    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=False)


    def rougeScore(self, reference_message, produced_message):
        scores = self.scorer.score(reference_message, produced_message)
        return scores['rouge1']

    @staticmethod
    def pearSon(d1, d2):
        a = np.array(d1)
        b = np.array(d2)
        return stats.pearsonr(a,b)
    @staticmethod
    def wilcoxon(d1, d2):
        a = np.array(d1)
        b = np.array(d2)
        return stats.wilcoxon(a, b)
    @staticmethod
    def hedgesg( d1, d2):
        # calculate the size of samples
        n1, n2 = len(d1), len(d2)
        # calculate the variance of the samples
        s1, s2 = std(d1, ddof=1), std(d2, ddof=1)
        # calculate the pooled standard deviation
        s = sqrt(((n1 - 1) * (s1 ** 2) + (n2 - 1) * (s2 ** 2)) / (n1 + n2 - 2))
        # calculate the means of the samples
        u1, u2 = mean(d1), mean(d2)
        N = n1 + n2
        biascorrect = ((N - 3) / (N - 2.25)) * (sqrt((N - 2) / N))
        # calculate the effect size
        return ((u1 - u2) / s) * biascorrect

    @staticmethod
    def resultTesting(objects, operations):
        projects = []
        for proj in objects:
            op_stat = []
            for op in operations:
                op_stat.append([proj[0].getValue(op), proj[1].getValue(op), proj[2].getValue(op), proj[3].getValue(op)])
            projects.append(op_stat)
        i = 0
        print(projects)
        for op in operations:
            print("tests for ", op)
            data1 = []
            data2 = []
            data3 = []
            data4 = []
            for project in projects:
                data1.append(project[i][0])
                data2.append(project[i][1])
                data3.append(project[i][2])
                data4.append(project[i][3])
            print("perfective and preventive ", Testing.hedgesg(data1, data2))
            print("perfective and adaptive ", Testing.hedgesg(data1, data3))
            print("perfective and corrective ", Testing.hedgesg(data1, data4))
            print("preventive and adaptive ", Testing.hedgesg(data2, data3))
            print("preventive and corrective ", Testing.hedgesg(data2, data4))
            print("adaptive and corrective ", Testing.hedgesg(data3, data4))
            i += 1

    @staticmethod
    def moTesting(stats):
        #let DELETE_COMMIT=0 NO_DELETE_COMMIT=1 DELETE_IN_MODULES=2 ALL_DELETE_MOS=3 CONTEXT_COMMIT_IMPACT=4 CNTEXT_FILE_IMPACT=5
        #DELETE_COMMIT=6 DELETE_FILES=7 OTHER_MOS_COMMIT=8 MOS_FILES=9 NO_DIRECT_COMMIT=10 NO_DIRECT_FILES=11
        # TEST_COMMIT=12 TEST_FILES=13 ONLY_IMPORT=14 ONLY_MODULES=15
        #           0           1               2               3               4               5           6                   7               8                   9                       10              11                     12          13          14           15          16
        FEATURES= ['TOTAL','DELETE_COMMIT', 'NO_DELETE', 'DELETE_MODULES', 'TOTAL_MOs', 'COMMIT_IMPACT', 'FILE_IMPACT', 'D_COMMIT_IMPACT', 'D_FILE_IMPACT', 'OTHER_COMMIT_IMPACT', 'OTHER_FILE_IMPACT', 'NODIRECT_COMMIT', 'NODIRECT_FILES', 'TEST', 'TEST_CLS', 'ONLY_IMPORT', 'ONLY_MOD']
        DATA=[]

        for stat in stats:
            print("----------------------------------------------------------")
            print(stat)
            element=[]
            length = len(FEATURES)
            for indx in range(0, length):
                element.append( int(stat[FEATURES[indx]]))

            element.append(round(element[8]/element[0], 3)) # Dcls/total
            element.append(round(element[10] / element[0], 3))  # Ocls/total
            element.append(round((element[6]- element[length-1])/ element[0], 3))  # contextual commits/total-modules only
            element.append(round((element[12] - element[length - 1]) / element[0],3))  # non contextual commits/total-modules only
            DATA.append(element)
        print("dcls vs ocls")
        print(Testing.hedgesg([val[17] for val in DATA], [val[18] for val in DATA]))
        print("context vs noncontext")
        print(Testing.hedgesg([val[19] for val in DATA], [val[20] for val in DATA]))

    @staticmethod
    def barDraw(objects, performance, y_label, title):
        import matplotlib.pyplot as plt
        plt.rcdefaults()
        import numpy as np
        import matplotlib.pyplot as plt
        y_pos = np.arange(len(objects))
        plt.bar(y_pos, performance, align='center', alpha=0.5)
        plt.xticks(y_pos, objects,fontsize=8, rotation=0)
        plt.ylabel(y_label)
        plt.title(title)

        plt.show()

    @staticmethod
    def graphLineDraw(objects, performance, y_label, title):
        import matplotlib.pyplot as plt
        plt.rcdefaults()
        import numpy as np
        import matplotlib.pyplot as plt
        plt.figure()
        plt.subplot(211)
        y_pos = np.arange(len(objects))
        plt.plot(y_pos,performance, color='gray', linestyle='dashed', marker='X', markerfacecolor='black')
        plt.xticks(y_pos, objects, fontsize=9, rotation=0)
        plt.ylim(ymin=50, ymax=80)
        plt.ylabel(y_label)
        plt.title(title)
        plt.show()

    @staticmethod
    def P_R(FP, FN, TP):
        print("Total extra wrong FP:", FP)
        print("Total could not rertieve FN:", FN)
        P = round(TP/(TP+FP), 4)
        R =round(TP/(TP+FN),4)
        return (P,R)

    @staticmethod
    def F_1(R, P):
        try:
            return round((2*P*R)/(P+R),4)*100
        except:
            return 0
    @staticmethod
    def misMatchEntities(tool_entities, manual_entities):
        if(len(tool_entities)>len(manual_entities)):
            try:
                return list(set(tool_entities) - set(manual_entities))
            except:
                print("manual", manual_entities)
                print("tool", tool_entities)
        else:
            try:
                return list(set(manual_entities)-set(tool_entities))
            except:
                print("manual", manual_entities)
                print("tool", tool_entities)
    @staticmethod
    def m2mToolPerformance(tool, manual):
        false_positive = 0 # extra instances that the toll predicts
        false_negative = 0 # rest of the instances within the manual set that the tool cannot predict
        true_positive = 0
        m2m_tool = tool
        m2m_manual = manual
        n_modules=m2m_manual.getNModuleSize()-m2m_tool.getNModuleSize()
        #TODO - value means tool is retreiving more false positives
        n_connected_classes=m2m_manual.getConnectClsSize() - m2m_tool.getConnectClsSize()
        n_disconnected_classes=m2m_manual.getDisconnectClsSize() - m2m_tool.getDisconnectClsSize()
        n_connected_modules=m2m_manual.getConnectModSize() - m2m_tool.getConnectModSize()
        n_connected_api=m2m_manual.getConnectApiSize() - m2m_tool.getConnectApiSize()
        n_disconnected_api=m2m_manual.getDisConnectApiSize() - m2m_tool.getDisConnectApiSize()
        n_disconnected_modules=m2m_manual.getDisConnectModSize() - m2m_tool.getDisConnectModSize()
        n_new_methods = m2m_manual.getNewMthdSize() - m2m_tool.getNewMthdSize()
        n_deleted_methods=m2m_manual.getDeletMthdSize() - m2m_tool.getDeletMthdSize()
        if(n_connected_classes>0):
            false_negative +=n_connected_classes
        else:
            false_positive += abs(n_connected_classes)
        if(n_connected_classes!=0):
            print("connect classes:",n_connected_classes, Testing.misMatchEntities(m2m_tool.n_connected_classes, m2m_manual.n_connected_classes))
        if(n_disconnected_classes>0):
            false_negative +=n_disconnected_classes
        else:
            false_positive += abs(n_disconnected_classes)
        if(n_disconnected_classes!=0):
            print("disconnect classes:",n_disconnected_classes,Testing.misMatchEntities(m2m_tool.n_disconnected_classes, m2m_manual.n_disconnected_classes))

        if(n_connected_modules>0):
            false_negative +=n_connected_modules
        else:
            false_positive += abs(n_connected_modules)
        if(n_connected_modules!=0):
            print("connect module:",n_connected_modules, Testing.misMatchEntities(m2m_tool.n_connected_modules, m2m_manual.n_connected_modules))

        if (n_disconnected_modules > 0):
            false_negative += n_disconnected_modules
        else:
            false_positive += abs(n_disconnected_modules)
        if (n_disconnected_modules != 0):
            print("disconnect module:",n_disconnected_modules,
                  Testing.misMatchEntities(m2m_tool.n_disconnected_modules, m2m_manual.n_disconnected_modules))
        if(n_connected_api>0):
            false_negative +=n_connected_api
        else:
            false_positive += abs(n_connected_api)
        if (n_connected_api != 0):
            print("connect api:",n_connected_api,
                  Testing.misMatchEntities(m2m_tool.n_connected_api, m2m_manual.n_connected_api))
        if (n_disconnected_api > 0):
            false_negative += n_disconnected_api
        else:
            false_positive += abs(n_disconnected_api)
        if (n_disconnected_api != 0):
            print("disconnect api:",n_disconnected_api,
                  Testing.misMatchEntities(m2m_tool.n_disconnected_api, m2m_manual.n_disconnected_api))
        if (n_new_methods > 0):
            false_negative += n_new_methods
        else:
            false_positive += abs(n_new_methods)
        if (n_new_methods != 0):
            print("new methods:",n_new_methods,
                  Testing.misMatchEntities(m2m_tool.n_new_methods, m2m_manual.n_new_methods))

        if (n_deleted_methods > 0):
            false_negative += n_deleted_methods
        else:
            false_positive += abs(n_deleted_methods)
        if (n_deleted_methods != 0):
            print("deleted methods:",n_deleted_methods,
                  Testing.misMatchEntities(m2m_tool.n_deleted_methods, m2m_manual.n_deleted_methods))

        # print("modules:",n_modules, "classes:",  "connected_modules:", n_connected_modules, "disconected_modules:", n_disconnected_modules,
        #       "connect_api:", n_connected_api, "disconnect_api:", n_disconnected_api, "connected_cls:", n_connected_classes, "disconnected_cls:", n_disconnected_classes, "new_method:",n_new_methods, "delete_method:",n_deleted_methods)
        return (false_positive, ((m2m_tool.total_m2m + m2m_tool.total_non_m2m)-false_negative), false_negative)
    @staticmethod
    def testAssociationRule():
        from category_analysis.model import Model


        data=[["ADD","import_add", "function_add"], ['DELETE','import_delete'], ['import_delete','import_add'], ['import_add','import_delete'], ['ADD','import_delete'], ['ADD','import_delete','DELETE'],['import_add','import_delete','DELETE']]
        outcome = [0,1,2,2, 2,3,3]
        for i in range(0, 7):
            print(data[i])
            if(outcome[i] == Model.codePredictionRule(data[i])):
                print("Test passed for: ", outcome[i])
            else:
                print("Not passed for: ", outcome[i])