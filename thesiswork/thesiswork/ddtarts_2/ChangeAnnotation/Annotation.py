from git import Repo
import csv
import nltk
from nltk.corpus import stopwords
import re
import gc
import time
import sys
import datetime
from pathlib import Path
import string
import operator
import itertools
import numpy as np
import collections
from preproces_mod.codechange import  JPMSMethod
from pydriller import RepositoryMining, GitRepository
from pydriller.domain.commit import Commit
from category_analysis.change import *
from similarity_analysis.clone_detection import *
csv.field_size_limit(2**16)
csv.field_size_limit(sys.maxsize)
commit_type = ["ADD","MODIFY","DELETE"]
allcategory = Change("All")



class Annotaion:
    def __init__(self,repo_path, filter_path, save_path, project_name=None):
        self.perfectiveO = Change("perfective")
        self.adaptiveO = Change("adaptive")
        self.preventiveO = Change("preventive")
        self.correctiveO = Change("corrective")
        self.repo_path = repo_path
        self.filter_path = filter_path
        self.commit_ids = []
        self.commit_msg = {}
        self.file_complexity = dict()
        self.save_path = save_path
        self.track_modification = {}
        self.test_cls = set()
        self.test_count=0
        self.f_impact = set()
        self.total_bug = 0
        self.bug_cls = set()
        self.contxt_bug = 0
        self.contxt_bug_cls = set()
        self.nocontxt_bug = 0
        self.nocontxt_bug_cls = set()
        self.buggy_cls = {}
        self.bug_later_count = 0
        self.no_direct_impact_cls = set()
        self.no_direct_impact_commit = 0
        self.project_name = project_name
        self.project_commits_stat = {}


    def annotateArchiChange(self, url):
        print("Repo: ", self.repo_path)
        fl = open(self.save_path, 'w')
        csv_write = csv.writer(fl)
        repo = Repo(self.repo_path)
        print("Wait commits downloading............")
        allcommits = repo.iter_commits(max_count=20000)
        print("loaded ")
        count = 0
        all_commits = []
        for com in allcommits:
            all_commits.append(com)
            count = count+1
            #print(count)
        #allcommits = RepositoryMining(self.repo_path, since=datetime.datetime(2011, 1, 1), to=datetime.datetime(2018, 1, 1)).traverse_commits()

        for com in all_commits:
            found=False
            for file in list(com.stats.files):
                if(".exe" in file or ".apk" in file or ".jar" in file or ".zip" in file or "chromedriver_" in file):
                    found=True
            if(found):
                continue
            commit = Commit(com,self.repo_path, None)
            #print(commit.hash)

            if(commit.hash not in self.commit_ids):
                print("not")

                for modification in commit.modifications:
                    if (modification.change_type.name is commit_type[0] or modification.change_type.name is commit_type[1]):
                        self.file_complexity[modification.new_path] = modification.complexity
                continue

            print("---------------------commits-----------------------------------------", commit.hash)
            del_change = False
            mod_change = False
            change = False
            import_found = False
            java_import = False
            for modification in commit.modifications:
                if(modification.change_type.name is commit_type[2]):
                    if(".java" in modification.filename):
                        del_change=True
                elif(self.checkTest(modification.new_path) and self.fileCheck(modification.filename)):

                    del_import = modification.diff.count("-import")
                    ad_import = modification.diff.count("+import")
                    if(modification.change_type.name is commit_type[0]):
                        change=True
                        self.file_complexity[modification.new_path] = modification.complexity
                    elif(modification.change_type.name is commit_type[1]):
                        pre_complexity = self.file_complexity.get(modification.new_path)
                        if(pre_complexity==None or pre_complexity!= modification.complexity):
                            mod_change = True
                        self.file_complexity[modification.new_path] = modification.complexity

                    if(del_import>0 or ad_import>0):
                        import_found = True
                        #modification.diff.
                        del_java = modification.diff.count("-import java.")
                        ad_java = modification.diff.count("+import java.")
                        if (del_import==del_java and ad_import==ad_java):

                            java_import = True


            get_time = time.strftime("%Y-%m-%d", time.gmtime(float(com.committed_date)))
            if(mod_change or change):
                if(import_found):
                    print("archi change")
                    if(java_import):
                        csv_write.writerow([url + "/" + commit.hash, commit.msg, com.stats.files, get_time, "no", "java import"])
                    else:
                        csv_write.writerow([url + "/" + commit.hash, commit.msg, com.stats.files, get_time, "yes", "nocheck"])
                else:
                    csv_write.writerow([url + "/" + commit.hash, commit.msg, com.stats.files, get_time, "no", "check"])
            elif del_change:
                print("probable change")
                csv_write.writerow([url + "/" + commit.hash, commit.msg, com.stats.files,get_time, "yes", "check"])
            else:
                csv_write.writerow([url + "/" + commit.hash, commit.msg, com.stats.files,get_time, "no", "nocheck"])
    def checkTest(self, strn):
        if ("test" not in strn and "Test" not in strn):
            return True
        return False

    def fileCheck(self, strn):
        if(".java" in strn):
            return True
        return False

    def commitOP(self, modification, types, tmp_class_impact):
        imports = None
        ischange = False
        if (modification.change_type.name is "MODIFY" or modification.change_type.name is "RENAME"):
            imports = self.parseModify(modification, True)
            # print("MODIFY: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
        elif (modification.change_type.name is "DELETE"):
            # print("DELETE: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
            types.add(modification.change_type.name)
            ischange = True
        elif (modification.change_type.name is "ADD"):
            # print("ADD: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
            types.add(modification.change_type.name)
            ischange = True
        if imports != None:
            for imprt in imports:
                if (imprt != ""):
                    ischange = True
                    types.add(imprt)
        if ischange:  # If has class connection change
            if modification.old_path:
                tmp_class_impact.add(modification.old_path)
                self.f_impact.add(modification.old_path)
            elif modification.new_path:
                self.f_impact.add(modification.new_path)
                tmp_class_impact.add(modification.new_path)

    def readNonContextFiles(self,):
        with open(self.project_name+".txt") as f:
            lines = [line.rstrip() for line in f]
            for line in lines:

                self.no_direct_impact_cls.add(line)

    def readProgramFile(self, dir):
        lines = []
        # print(dir)
        with open(dir) as f:
            for line in f:
                if(self.findComment(line)==False):
                    lines.append(line.rstrip())
                else:
                    pass
                    # print(line)
            # lines = [line.rstrip() for line in f]
        #print(lines)
        return lines
    def findComment(self, word):
        if (word.lstrip(' ').find('//', 0) == 0):
            return True
        if (word.lstrip(' ').find('/*', 0) == 0):
            return True
        if (word.lstrip(' ').find('*', 0) == 0):
            return True
        if(word == '\n'):
            return True
        if (word.lstrip(' ').find('*/')>-1):
            return True
        return False

    def excludeComment(self, method):
        active_code_statement = []

        for line in method:
            if(line=="\n"):
                continue
            if (self.findComment(line) == False):
                active_code_statement.append(line)
        return active_code_statement

    def parseModuleFile(self, parsed_lines):
        parsed_content = []
        for add_tuple in parsed_lines:
            name_part = add_tuple
            if (name_part.lstrip(' ').find('//', 0) == 0):
                None
            else:

                # need to remove comments
                only_modules = name_part.split('//')[0].strip().strip(";").strip("{").strip( # remove unnecessary string
                    "}").replace('open ', ' ').replace(',', ' ').replace('\n', '')
                if (only_modules != ''):
                    is_module_operation = True
                    # print("Added: ", only_modules)
                    ## spliting a text having: operation_name module_name
                    module_operation = only_modules.split()
                    parsed_content.append(module_operation)
        return parsed_content

    def findLink(self, mod_contnt1, mod_contnt2):
        try:

            mod_name1 = mod_contnt1[0][len(mod_contnt1[0])-1].strip(' ')
            mod_name2= mod_contnt2[0][len(mod_contnt2[0])-1].strip(' ')

            # print(mod_name1, mod_name2)
            cnt1 = itertools.chain.from_iterable(mod_contnt1)
            flat_cnt1 = [x.strip(' ') for x in cnt1]
            cnt2 = itertools.chain.from_iterable(mod_contnt2)
            flat_cnt2 = [x.strip(' ') for x in cnt2]
            if mod_name2 in flat_cnt1:
                return True
            if mod_name1 in flat_cnt2:
                return True
        except:
            pass
        return False

    def readCsv(self):
        csvfile = open(self.filter_path, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            id = row[0].split()[0]
            parts =id.split("/")
            ID = parts[len(parts) - 1]
            self.commit_msg[ID]=row
            self.commit_ids.append(ID)
        csvfile.close()

    def getCommitSamples(self, change_idx=4):
        csvfile = open(self.filter_path, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        changed_commit = ChangedCommit()
        changed_commit.project_name = self.project_name
        for row in reader:
            try:
                id = row[0].split()[0]
                parts =id.split("/")
                ID = parts[len(parts) - 1]
                changed_commit.samples.append([ID, row[change_idx]])
                self.commit_msg[ID]=row
                self.commit_ids.append(ID)
            except:
                pass
        csvfile.close()
        return changed_commit

    def separateIDFromURL(self):
        csvfile = open(self.filter_path, 'r', encoding="utf8", errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            parts = row[0].split("/")
            ID = parts[len(parts) - 1]
            self.commit_ids.append(ID)
        csvfile.close()

    def getBugsAndLaterImpact(self):
        other_commit = 0
        print(self.repo_path)
        f_impact = set()
        class_impact_others = set()
        co_impact_others = 0
        count=0
        print("Wait commits downloading............")

        allcommits = RepositoryMining(self.repo_path, since=datetime.datetime(2017, 7, 1), to=datetime.datetime(2019, 12, 25)).traverse_commits()
        test_count = 0
        is_bug = False
        bug_count = 0
        for commit in allcommits:
            tmp_class_impact = set()
            is_bug = self.bugFixDetect(commit.msg)
            if(is_bug):
                bug_count +=1

            else:
                continue
            #print("project path: " + row[0])
            for modification in commit.modifications:

                 if (self.fileCheck(modification.filename)):
                    fil_path =self.existedPath(modification.new_path, modification.old_path)
                    if(self.checkTest(fil_path)):
                        #types.append(modification.change_type.name)
                        tmp_class_impact.add(fil_path)
                        if(is_bug):
                            if(fil_path in self.no_direct_impact_cls):
                                self.bug_later_count +=1
                    else:
                        has_test = True

            for itm in tmp_class_impact:
                 class_impact_others.add(itm)

        print("------------------Stat ----------------------")

        stat = {}
        stat["BF"] = bug_count
        stat["BC"] = len(class_impact_others) # number of classes impacted for connections that do not contain delete within a module
        stat["LATER"] = self.bug_later_count
        print(stat)
        print("----------------------------------------------------------")

    def commitForUsualArchi(self):
        other_commit = 0
        print(self.repo_path)
        f_impact = set()
        class_impact_others = set()
        co_impact_others = 0
        count=0
        # repo = Repo(self.repo_path)

        print("Wait commits downloading............")
        # allcommits = repo.iter_commits()

        # count = 0
        # all_commits = []
        # for com in allcommits:
        #     com.committed_date
        #     all_commits.append(com)
        allcommits = RepositoryMining(self.repo_path, since=datetime.datetime(2017, 7, 1), to=datetime.datetime(2019, 12, 25)).traverse_commits()
        #print("loaded ")
        has_test = False
        test_count = 0
        is_bug = False
        bug_count = 0
        for commit in allcommits:

            #commit = Commit(com,self.repo_path, None)
            if(commit.hash in self.commit_ids):
                # print("Skipped:")
                continue
            types = set()
            tmp_class_impact = set()
            tmp_class_test = set()
            for modification in commit.modifications:

                 if (self.fileCheck(modification.filename)):
                    fil_path =None
                    if(modification.new_path != None):
                        fil_path = modification.new_path
                    elif (modification.old_path != None):
                        fil_path = modification.old_path

                    if(self.checkTest(fil_path)):
                        #types.append(modification.change_type.name)
                        self.commitOP(modification, types, tmp_class_impact)
                        # imports = None
                        # ischange = False
                        # if(modification.change_type.name is "RENAME"):
                        #     # print("NAME: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
                        #     types.add(modification.change_type.name)
                        #     ischange = True
                        # elif(modification.change_type.name is "MODIFY" or modification.change_type.name is "RENAME"):
                        #     imports = self.parseModify(modification)
                        #     # print("MODIFY: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
                        # elif (modification.change_type.name is "DELETE"):
                        #     # print("DELETE: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
                        #     types.add(modification.change_type.name)
                        #     ischange = True
                        # elif (modification.change_type.name is "ADD"):
                        #     # print("ADD: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
                        #     types.add(modification.change_type.name)
                        #     ischange = True
                        # if imports != None:
                        #     for imprt in imports:
                        #         if(imprt != ""):
                        #             ischange = True
                        #             types.add(imprt)
                        # if ischange:
                        #     if modification.old_path:
                        #         tmp_class_impact.add(modification.old_path)
                        #         f_impact.add(modification.old_path)
                        #     elif modification.new_path:
                        #         f_impact.add(modification.new_path)
                        #         tmp_class_impact.add(modification.new_path)
                    else:
                        has_test = True
                        tmp_class_test.add(fil_path)
            if types != set():

               co_impact_others += 1
               if(has_test):
                   test_count +=1
                   self.test_count +=1
                   self.test_cls.update(tmp_class_test)
               for itm in tmp_class_impact:
                   class_impact_others.add(itm)
               other_commit += 1


               count+=1

        print("Total commit: ",count)
        print("------------------Stat ----------------------")
        total = 0

        stat = {}

        stat["OCI"] = co_impact_others # number of commits impacted class connections that do not contain delete within a module
        stat["OFI"] = len(class_impact_others) # number of classes impacted for connections that do not contain delete within a module
        stat["TEST"] = self.test_count
        stat["TEST_CLS"] = len(self.test_cls)
        print(stat)
        print("----------------------------------------------------------")
    def laterBugInfo(self):
        print("Later bug:", self.bug_later_count)
    def commitFromUrl(self):
        csvfile = open(self.filter_path, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        gr = GitRepository(self.repo_path)
        print(self.repo_path)
        fl = open(self.save_path, 'w')
        csv_write = csv.writer(fl)
        co_impact = 0
        f_impact = set()
        class_impact_others = set()
        count=0
        cat_indx = 3
        for row in reader:
            is_module_operation = False
            parts = row[0].split("/")
            ID= parts[len(parts)-1]
            self.commit_ids.append(ID)
            commit = gr.get_commit(ID)
            types = set()
            unique = set()
            tmp_class_impact = set()
            ischange = False
            change_object = None
            if ("perfective" in row[cat_indx].lower()):
                # print(word)
                change_object = self.perfectiveO

            if ("corrective" in row[cat_indx].lower()):
                change_object = self.correctiveO
            if ("adaptive" in row[cat_indx].lower()):
                change_object = self.adaptiveO
            if ("preventive" in row[cat_indx].lower()):
                change_object = self.preventiveO

            #print("project path: " + row[0])
            for modification in commit.modifications:


                if(self.fileCheck(modification.filename)):
                    fil_path =None
                    if(modification.new_path != None):
                        fil_path = modification.new_path
                    elif (modification.old_path != None):
                        fil_path = modification.old_path
                    if(self.checkTest(fil_path)):
                        #types.append(modification.change_type.name)
                        #modification.removed
                        imports = None
                        ischange = False
                        if(modification.change_type.name is "RENAME"):
                            # print("NAME: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
                            types.add(modification.change_type.name)
                            unique.add(modification.change_type.name)
                            ischange = True
                        elif(modification.change_type.name is "MODIFY"):
                            imports = self.parseUsualModify(gr, modification,commit.committer_date)
                            # print("MODIFY: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
                        elif (modification.change_type.name is "DELETE"):
                            # print("DELETE: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
                            types.add(modification.change_type.name)
                            ischange = True
                            unique.add(modification.change_type.name)
                        elif (modification.change_type.name is "ADD"):
                            # print("ADD: old--" + str(modification.old_path) + " new----" + str(modification.new_path))
                            types.add(modification.change_type.name)
                            unique.add(modification.change_type.name)
                            ischange = True
                        if imports != None:
                            for imprt in imports:
                                if(imprt != ""):
                                    ischange = True
                                    types.add(imprt)
                                    if("add_" in imprt):
                                        unique.add("function_add")
                                    elif("del_" in imprt):
                                        unique.add("function_delete")
                                    else:
                                        unique.add(imprt)
                        if ischange:
                            if modification.old_path:
                                tmp_class_impact.add(modification.old_path)
                                f_impact.add(modification.old_path)
                            elif modification.new_path:
                                f_impact.add(modification.new_path)
                                tmp_class_impact.add(modification.new_path)
            if(True):
                change_object.setTotal(1)
                allcategory.setTotal(1)
                if types != set():
                    co_impact += 1
                if(unique!=set()):
                    change_object.setOperation(unique)
                    allcategory.setOperation(unique)
                change_object.setImpactedClasses(tmp_class_impact)
                allcategory.setImpactedClasses(tmp_class_impact)
                count+=1
                row.append(types)
                row.append(unique)
                csv_write.writerow(row)
        # print("------------------Modules operation ----------------------")
        # for name in collections.OrderedDict(sorted(self.modules.items(), key=operator.itemgetter(1),reverse=True)):
        #     print(name+": "+ str(self.modules[name]))
        print("Total commit: ",count)

        csvfile.close()
        fl.close()

    #this method will find whether a imported class is really used in added code or deleted code
    def findImportedClass(self,parsed_lines, imported, modification):
        source_code = modification.source_code
        deleted = parsed_lines["deleted"]
        import_deletes = [line[1] for line in deleted if line[1].find('import', 0) == 0]
        added = parsed_lines["added"]
        import_added = [line[1] for line in added if line[1].find('import', 0) == 0]
        methods = modification.methods
    #
    # Tuple: first element code line, seoncd element code
    def getcodeLines(self, parsed_lines):
        deleted = parsed_lines["deleted"]
        deleted_lines = [line[0] for line in deleted]
        added = parsed_lines["added"]
        added_lines = [line[0] for line in added]
        return(added_lines, deleted_lines)

    def matchMethodLocs(self, locs, changes):
        return set(locs) <= set(changes)
    def onlyMthdName(self,name):
        parts = name.split("::")
        return parts[len(parts)-1]

    #TODO -- this method attempt to extract probable deleted, and added methods from the boundary of the two versions of a file
    def extractModifiedMethods(self, gr,modification, cm_date, native=False):
        ops = []
        method_mod =False
        methods = []
        added_methods = []
        deleted_methods = []
        source_code_before = modification.source_code_before.splitlines()
        source_code_after = modification.source_code.splitlines()
        added_lines ,deleted_lines = self.getcodeLines(modification.diff_parsed)

        def getnums(s, e):
            return (np.arange(s, e))
        for mthd in modification.methods:
            added_locs = getnums(mthd.start_line, mthd.end_line) # get all the locations of the statements of the method
            if(self.matchMethodLocs(added_locs, added_lines)):
                jmthd = JPMSMethod()
                jmthd.setName(self.onlyMthdName(mthd.name))
                jmthd.setCode(source_code_after[mthd.start_line-1: mthd.end_line])
                added_methods.append(jmthd)


        commits = gr.get_commits_modified_file(modification.old_path)
        file_commits = []
        #print(cm_date)
        #get all the previous commits for this file
        for comm in commits:
            cm = gr.get_commit(comm)

            if(cm.committer_date < cm_date):
                file_commits.append(cm )
                break
        classwith_mthds = []
        if(len(file_commits)>0):
            for modi in file_commits[0].modifications: # first commit is probably the latest commit
                history_path=None
                if(modi.new_path):
                    history_path = modi.new_path
                else:
                    history_path = modi.old_path
                if (history_path == modification.old_path):
                    for mtd in modi.methods:

                        classwith_mthds.append( mtd)
            #after_mthds = []
            #
            # for mthd in modification.methods:
            #     found = False
            #     for prev_mthd in classwith_mthds:
            #         if(prev_mthd.name==mthd.name):
            #             found = True
            #
            #         if(mthd.end_line == prev_mthd.end_line and  mthd.start_line == prev_mthd.start_line and mthd.top_nesting_level == prev_mthd.top_nesting_level and len(mthd.parameters) == len(prev_mthd.parameters)):
            #             found =True
            #
            #     if(found == False):
            #         methods.append("add_" + mthd.name)
            # for mthd in classwith_mthds:
            #     found = False
            #     for prev_mthd in modification.methods:
            #         if (prev_mthd.name == mthd.name):
            #             found = True
            #
            #         if(mthd.end_line == prev_mthd.end_line and  mthd.start_line == prev_mthd.start_line and mthd.top_nesting_level == prev_mthd.top_nesting_level and  len(mthd.parameters) == len(prev_mthd.parameters)):
            #             found =True
            #
            #     if(found==False):
            #         methods.append("del_" + mthd.name)

            for mthd in classwith_mthds:
                mod_locs = getnums(mthd.start_line, mthd.end_line)
                if (self.matchMethodLocs(mod_locs, deleted_lines)):
                    jmthd = JPMSMethod()
                    jmthd.setName(self.onlyMthdName(mthd.name))
                    jmthd.setCode(source_code_before[mthd.start_line - 1: mthd.end_line])
                    deleted_methods.append(jmthd)

        return [added_methods,deleted_methods]

    #TODO -- experimental method attempt to extract probable deleted, and added methods from the boundary of the two versions of a file
    def experimentalExtractMethods(self, gr,modification, cm_date, native=False):
        ops = []
        method_mod =False
        methods = []
        added_methods = []
        deleted_methods = []

        def getnums(s, e):
            return (np.arange(s, e))

        added_lines, deleted_lines = self.getcodeLines(modification.diff_parsed)
        modification_path = None
        if (modification.new_path):
            modification_path = modification.new_path
        else:
            modification_path = modification.old_path
        parts = modification_path.split("/")
        class_name = parts[len(parts) - 1].split(".")[0]
        # print(class_name)
        if(modification.source_code != None):
            source_code_after = modification.source_code.splitlines()

            # print("Total method after modification -->", len(modification.methods))
            for mthd in modification.methods:
                added_locs = getnums(mthd.start_line, mthd.end_line) # get all the locations of the statements of the method
                if(self.matchMethodLocs(added_locs, added_lines)):
                    jmthd = JPMSMethod()
                    # print("Added --->>", added_locs)
                    jmthd.setName(self.onlyMthdName(mthd.name))
                    if(class_name == jmthd.name):
                        jmthd.setType(0)
                    jmthd.setCode(source_code_after[mthd.start_line-1: mthd.end_line])
                    # print("Method code -->> ", jmthd.code)
                    jmthd.setAsBlock(CodeToToekn.codeToken(self.excludeComment(jmthd.code)))
                    added_methods.append(jmthd)



        #after_mthds = []
        #
        # for mthd in modification.methods:
        #     found = False
        #     for prev_mthd in classwith_mthds:
        #         if(prev_mthd.name==mthd.name):
        #             found = True
        #
        #         if(mthd.end_line == prev_mthd.end_line and  mthd.start_line == prev_mthd.start_line and mthd.top_nesting_level == prev_mthd.top_nesting_level and len(mthd.parameters) == len(prev_mthd.parameters)):
        #             found =True
        #
        #     if(found == False):
        #         methods.append("add_" + mthd.name)
        # for mthd in classwith_mthds:
        #     found = False
        #     for prev_mthd in modification.methods:
        #         if (prev_mthd.name == mthd.name):
        #             found = True
        #
        #         if(mthd.end_line == prev_mthd.end_line and  mthd.start_line == prev_mthd.start_line and mthd.top_nesting_level == prev_mthd.top_nesting_level and  len(mthd.parameters) == len(prev_mthd.parameters)):
        #             found =True
        #
        #     if(found==False):
        #         methods.append("del_" + mthd.name)
        if(modification.source_code_before != None):
            # commits = gr.get_commits_modified_file(modification.old_path)
            # file_commits = []
            # # print(cm_date)
            # # get all the previous commits for this file
            # for comm in commits:
            #     cm = gr.get_commit(comm)
            #
            #     if (cm.committer_date < cm_date):
            #         file_commits.append(cm)
            #         break
            # classwith_mthds = []
            # if (len(file_commits) > 0):
            #     for modi in file_commits[0].modifications:  # first commit is probably the latest commit
            #         history_path = None
            #         if (modi.new_path):
            #             history_path = modi.new_path
            #         else:
            #             history_path = modi.old_path
            #         if (history_path == modification.old_path):
            #             for mtd in modi.methods:
            #                 classwith_mthds.append(mtd)
            # if()
            classwith_mthds = modification.methods_before
            # print("Total method in the last version modification -->", len(classwith_mthds))
            source_code_before = modification.source_code_before.splitlines()
            for mthd in classwith_mthds:
                mod_locs = getnums(mthd.start_line, mthd.end_line)
                if (self.matchMethodLocs(mod_locs, deleted_lines)):
                    jmthd = JPMSMethod()
                    jmthd.setName(self.onlyMthdName(mthd.name))
                    # print("Deleted lines -->", mod_locs)
                    jmthd.setCode(source_code_before[mthd.start_line - 1: mthd.end_line])
                    # print("Deleted method -->", jmthd.code)
                    jmthd.setAsBlock(CodeToToekn.codeToken(self.excludeComment(jmthd.code)))
                    deleted_methods.append(jmthd)
                    if (class_name == jmthd.name):
                        jmthd.setType(0)
        final_added_methods=[]
        #final_deleted_methods = []
        del_cloned_methds = []
        for ad_mthd in added_methods:
            found =False
            for del_mthd in deleted_methods:
                if(Clone(0.70).isClone(ad_mthd.asblock,del_mthd.asblock)):
                    found = True
                    print("Clone: ",ad_mthd.name, del_mthd.name)
                    del_cloned_methds.append(del_mthd)

            if(found==False):
                final_added_methods.append(ad_mthd)
        for cloned in del_cloned_methds:
            try:
                deleted_methods.remove(cloned)
            except Exception as ee:
                print(ee)
        # print("final list added--")
        # for ad_m in final_added_methods:
        #     print(ad_m.name, ad_m.m_type, ad_m.asblock.tokenmap.keys())
        # print("final list deleted--")
        # for d_m in deleted_methods:
        #     print(d_m.name, d_m.m_type, d_m.asblock.tokenmap.keys())
        return [final_added_methods,deleted_methods]


    def parseUsualModify(self, gr,modification, cm_date, native=False):
        ops = []
        method_mod =False
        methods = []
        source_code = modification.source_code_before
        commits = gr.get_commits_modified_file(modification.old_path)
        file_commits = []
        #print(cm_date)
        #get all the previous commits for this file
        for comm in commits:
            cm = gr.get_commit(comm)

            if(cm.committer_date < cm_date):
                file_commits.append(cm )
        classwith_mthds = []
        if(len(file_commits)>0):
            for modi in file_commits[0].modifications: # first commit is probably the latest commit
                history_path=None
                if(modi.new_path):
                    history_path = modi.new_path
                else:
                    history_path = modi.old_path
                if (history_path == modification.old_path):
                    for mtd in modi.methods:

                        classwith_mthds.append( mtd)
            #after_mthds = []

            for mthd in modification.methods:
                found = False
                for prev_mthd in classwith_mthds:
                    if(prev_mthd.name==mthd.name):
                        found = True

                    if(mthd.end_line == prev_mthd.end_line and  mthd.start_line == prev_mthd.start_line and mthd.top_nesting_level == prev_mthd.top_nesting_level and len(mthd.parameters) == len(prev_mthd.parameters)):
                        found =True

                if(found == False):
                    methods.append("add_" + mthd.name)
            for mthd in classwith_mthds:
                found = False
                for prev_mthd in modification.methods:
                    if (prev_mthd.name == mthd.name):
                        found = True

                    if(mthd.end_line == prev_mthd.end_line and  mthd.start_line == prev_mthd.start_line and mthd.top_nesting_level == prev_mthd.top_nesting_level and  len(mthd.parameters) == len(prev_mthd.parameters)):
                        found =True

                if(found==False):
                    methods.append("del_" + mthd.name)

                # if(mthd.fan_in>0):
                #     print("Fan in: "+ mthd.fan_in)
                # if (mthd.fan_out > 0):
                #     print("Fan out: " + mthd.fan_out)
        del_import = modification.diff.count("-import")
        ad_import = modification.diff.count("+import")
        if (del_import > 0 or ad_import > 0):
            import_found = True
            # modification.diff.
            if(native==False):
                del_java = modification.diff.count("-import java.")
                ad_java = modification.diff.count("+import java.")
                if (del_import == del_java and ad_import == ad_java):
                    java_import = True
                else:
                    if(ad_import!=ad_java):
                        ops.append("import_add")
                    if(del_import != del_java):
                        ops.append("import_delete")
            else:
                if (ad_import >0):
                    ops.append("import_add")
                if (del_import >0):
                    ops.append("import_delete")
        for mname in methods:
            ops.append(mname)
        return ops

    def checkImportDiff(self, a_imports, d_imports):
        matched = True
        for a_item in a_imports:
            parts = a_item
            if (".*;" in a_item):
                parts = a_item.strip("*;")
            found = False
            for d_item in d_imports:
                if (parts.strip('+') in d_item.strip('-')):
                    found = True
            if (found == False):
                return False

        return matched

    def importMatch(self, a_item, d_item):
        if (".*" in d_item):
            if (d_item.replace(".*;", "") in a_item):
                return True
            else:
                return False
        if (".*" in a_item):
            if (a_item.replace(".*;", "") in d_item):
                return True
            else:
                return False

        elif(a_item == d_item):
            return True

        else:
            return False

    def onlyDifferentiateImports(self, a_imports, d_imports):
        matched = True
        temp_a_import = []
        temp_d_import=[]
        for a_item in a_imports:
            parts = a_item
            found = False
            for d_item in d_imports:
                if(self.importMatch(parts,d_item)):
                    found = True
                    break
            if (found == False):
                temp_a_import.append(a_item)
        for d_item in d_imports:
            parts = d_item
            found = False
            for a_item in a_imports:
                if(self.importMatch(parts, a_item)):
                    found=True
                    break
            if (found == False):
                temp_d_import.append(d_item)

        return (temp_a_import, temp_d_import)
    #check imports are just shrinking with .* or change locations

    def similarImportChange(self, parsed_lines):
        deleted = parsed_lines["deleted"]

        import_deletes = [line[1] for line in deleted if line[1].find('import', 0) == 0]
        added = parsed_lines["added"]
        import_added = [line[1] for line in added if line[1].find('import', 0) == 0]
        if(len(import_deletes) <1 or len(import_added) <1):
            return False
        return self.checkImportDiff(import_added,import_deletes)

    def onlyImport(self, modification,gr):
        # if(modification.new_path == "modBase/src/org/aion/base/AionTxExecSummary.java"):
        #     print("")
        parsed_lines = modification.diff_parsed
        add_line_count = modification.diff.count("+\n")
        del_line_count = modification.diff.count("-\n")
        add_slash_count = modification.diff.count("\\+[\s]*//") + modification.diff.count("\\+[\s]*/")
        add_at_count =  modification.diff.count("+@")
        del_slash_count = modification.diff.count("-[\s]*//") + modification.diff.count("-[\s]*/")
        del_at_count = modification.diff.count("+@")
        add_todo_count = len(re.findall("\\+[\s]*TODO", modification.diff))  # modification.diff.count("+ *")
        del_todo_count = len(re.findall("-[\s]*TODO", modification.diff))  # modification.diff.count("- *")
        add_star_count = len(re.findall("\\+[\s]*\\*", modification.diff)) #modification.diff.count("+ *")
        del_star_count = len(re.findall("-[\s]*\\*", modification.diff)) #modification.diff.count("- *")
        add_pack_count =  modification.diff.count("+package")
        del_pack_count = modification.diff.count("-package")
        del_import_count = modification.diff.count("-import")
        ad_import_count = modification.diff.count("+import")
        del_count = len(parsed_lines["deleted"])
        ad_import_count = ad_import_count + (
                    add_at_count + add_slash_count + add_pack_count + add_star_count + add_line_count + add_todo_count)
        del_count = del_count - (del_at_count + del_slash_count + del_pack_count + del_star_count + del_line_count+del_todo_count)
        ad_count = len(parsed_lines["added"])
        fil_path = None
        if (modification.new_path != None):
            fil_path = modification.new_path
        elif (modification.old_path != None):
            fil_path = modification.old_path
        # print(fil_path, ":: ",
        #       "ad_import_count, add_pack_count, add_slash_count, add_star_count, add_at_count, add_todo_count:, del_import_count, del_pack_count, del_slash_count, del_star_count, del_at_count, del_to_do")
        # print("Add count ", ad_count)
        # print("Del count ", del_count)
        # print(ad_import_count, add_pack_count, add_slash_count, add_star_count, add_at_count, ":", del_import_count,
        #       del_pack_count, del_slash_count, del_star_count, del_at_count)

        if (del_import_count == del_count and ad_import_count == ad_count):
            # print("True")
            return True
        # print("False")
        return False

    def parseModify(self, modification, native=False):
        ops = []

        for mthd in modification.methods:
            if(mthd.fan_in>0):
                print("Fan in: "+ mthd.fan_in)
            if (mthd.fan_out > 0):
                print("Fan out: " + mthd.fan_out)
        del_import = modification.diff.count("-import")
        ad_import = modification.diff.count("+import")
        if (del_import > 0 or ad_import > 0):
            import_found = True
            # modification.diff.
            if(native==False):
                del_java = modification.diff.count("-import java.")
                ad_java = modification.diff.count("+import java.")
                if (del_import == del_java and ad_import == ad_java):
                    java_import = True
                else:
                    if(ad_import!=ad_java):
                        ops.append("import_add")
                    if(del_import != del_java):
                        ops.append("import_delete")
            else:
                if (ad_import >0):
                    ops.append("import_add")
                if (del_import >0):
                    ops.append("import_delete")
        return ops
    def getChangeOPbjects(self):
        self.perfectiveO.normalize()
        self.preventiveO.normalize()
        self.adaptiveO.normalize()
        self.correctiveO.normalize()
        print("pkg impact perefe prev, adap, correc")
        print(self.packageImpact(self.perfectiveO),self.packageImpact(self.preventiveO),self.packageImpact(self.adaptiveO), self.packageImpact(self.correctiveO))

        print("class impact perefe prev, adap, correc")
        print(len(self.perfectiveO.classes_impacted),len(self.preventiveO.classes_impacted),len(self.adaptiveO.classes_impacted), len(self.correctiveO.classes_impacted))
        return (self.perfectiveO,self.preventiveO,self.adaptiveO, self.correctiveO)

    def packageImpact(self, cat_obj):
        pkg = set()
        for cls_fl in cat_obj.classes_impacted:
            parts = cls_fl.split("/")
            pkg.add(cls_fl.strip(parts[len(parts)-1]))
        return len(pkg)

    def bugFixDetect(self, txt):
        # print("bug induce detection")
        score = 0
        match = re.findall(r'bug[# \t]*[0-9]+', txt)
        score = len(match)
        # print(match)
        match = re.findall(r'pr[ #\t]*[0-9]+', txt)
        score += len(match)
        # print(match)
        match = re.findall(r'(fix)[e]*[ds]*?', txt)
        score += len(match)
        match = re.findall(r'fixed point?', txt)
        score -= len(match)
        # print(match)
        match = re.findall(r'bug[\w]?', txt)
        score += len(match)
        # print(match)
        match = re.findall(r'defect[\w]?', txt)
        score += len(match)
        # print(match)
        match = re.findall(r'patch?', txt)
        score += len(match)
        if (score > 0):
            # print(txt)
            return True
        return False

    def csvContent(self):
        csvfile = open(self.filter_path, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        buggy = 0
        for row in reader:
            if(self.bugFixDetect(row[1])):
                buggy +=1
        print("Bugs ", buggy)
    # if date1 is small
    def dateCompare(self, date1, date2):
        from datetime import datetime
        date_object1 = datetime.strptime(date1, '%Y-%m-%d').date()

        date_object2 = datetime.strptime(date2, '%Y-%m-%d').date()
        if (date_object1 < date_object2):
            return True
        return False

    def buggyClass(self, cls, time_date):
        cls_date = self.buggy_cls.get(cls)
        if(cls_date is None):
            self.buggy_cls[cls] = time_date
        else:
            if(self.dateCompare(time_date, cls_date)):
                self.buggy_cls[cls] = time_date

    def existedPath(self, new_path, old_path):
        if (new_path != None):
            return new_path
        elif (old_path != None):
            return old_path
    def fileInBugs(self, cls, time_date):
        cls_date = self.buggy_cls.get(cls)
        if (cls_date is None):
            pass
        else:
            if (self.dateCompare(cls_date, time_date)):
                self.bug_later_count +=1

    def commitIdsInRange(self):
        fl = open(self.save_path, 'w')
        csv_write = csv.writer(fl)
        print("Wait commits downloading............")
        allcommits = RepositoryMining(self.repo_path, since=datetime.datetime(2017, 7, 1), to=datetime.datetime(2020, 6, 30)).traverse_commits()
        for commit in allcommits:
            get_time = commit.committer_date
            csv_write.writerow([commit.hash, get_time])


