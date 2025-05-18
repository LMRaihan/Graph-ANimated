import sys
import git
import csv
from pydriller import RepositoryMining, GitRepository
from pydriller.domain.commit import Commit
from category_analysis.change import *
csv.field_size_limit(2**16)
csv.field_size_limit(sys.maxsize)
from ChangeAnnotation.jpms import  ModuleAnnotate
from preproces_mod.codechange import *
from postprocess.semanticop import *
commit_type = ["ADD","MODIFY","DELETE", "RENAME"]

class CommitState:
    def __init__(self, id):
        self.id = id
        self.packages = []
        self.jpms = []
        self.module_modify = []
        self.module_add = []
        self.module_delete = []
        self.module_rename = []
        self.mo_add = {}
        self.mo_delete = {}
        self.class_add = []
        self.class_delete= []
        self.class_rename = []
        self.class_modify=[]
        self.class_context = []
        self.class_noncontext = []
        self.class_bug_context = []
        self.class_bug_noncontext = []
        self.test_class = []
        self.only_import =[]
        self.import_dependency = {}

        self.a2aClass = []


class PrimaryChange(ModuleAnnotate):
    def __init__(self,repo_path=None, filter_path=None, save_path=None, project_name=None):
        super().__init__(repo_path, filter_path, save_path, project_name)
        self.commits_state=[]
        self.commit_cat = dict()
        self.jpmshot = {}
        self.change_relations = []
        self.classhot = {}
        self.perfectiveO = ModuleChange("perfective")
        self.correctiveO = ModuleChange("corrective")
        self.preventiveO = ModuleChange("preventive")
        self.adaptiveO = ModuleChange("adaptive")
        self.codechange_relations = []
        self.detected = None
        self.design_modules = [{},{},{},{}]
        self.dg = []
        self.commit_identifiers = {}
        self.sudo_id=1
        self.commits = []
        self.filtered_commits = []
        self.total_commit = 0
        self.archi_commit = 0

    def jpmsModules(self):

        from os import walk

        f = set()
        pkg = set()
        # print(self.repo_path)
        for (dirpath, dirnames, filenames) in walk(self.repo_path):
            ifjava=False
            for filename in filenames:

                if('module-info.java' in filename):
                    f.add(dirpath+"/"+filename)
                elif(".java" in filename or ".kt" in filename):
                    ifjava=True
            if(ifjava):
                pkg.add(dirpath)


        return (f,pkg)

    def getRelativePackage(self, class_file):
        relative_cls = class_file.replace(self.repo_path+"/","")
        parts = relative_cls.split("/")
        relative_pack = relative_cls.replace(parts[len(parts)-1],"")
        # print(relative_pack)
        return relative_pack

    def getIncludeDependency(self, modification):

        imprts = []

        del_import = modification.diff.count("-import")
        ad_import = modification.diff.count("+import")
        add_pack_count = modification.diff.count("+package")
        del_pack_count = modification.diff.count("-package")
        if ((del_import + ad_import + add_pack_count + del_pack_count) > 0):
            for imprt in modification.diff.split('\n'):
                # add_line_count = modification.diff.count("+\n")
                # del_line_count = modification.diff.count("-\n")
                # add_slash_count = modification.diff.count("\\+[\s]*//") + modification.diff.count("\\+[\s]*/")
                # add_at_count = modification.diff.count("+@")
                # del_slash_count = modification.diff.count("-[\s]*//") + modification.diff.count("-[\s]*/")
                # del_at_count = modification.diff.count("+@")
                # add_todo_count = len(re.findall("\\+[\s]*TODO", modification.diff))  # modification.diff.count("+ *")
                # del_todo_count = len(re.findall("-[\s]*TODO", modification.diff))  # modification.diff.count("- *")
                # add_star_count = len(re.findall("\\+[\s]*\\*", modification.diff))  # modification.diff.count("+ *")
                # del_star_count = len(re.findall("-[\s]*\\*", modification.diff))
                if(not self.findComment(imprt)):
                    if (imprt.find('-import', 0) == 0):
                        imprts.append(imprt.replace("-",""))
                    if (imprt.find('+import', 0) == 0):
                        imprts.append(imprt.replace("+",""))
                    # if (imprt.find('-package', 0) == 0):
                    #     imprts.append(imprt)
                    # if (imprt.find('+package', 0) == 0):
                    #     imprts.append(imprt)

        return imprts

    def isImportInStatement(self, imprt, statement):
        if(",*" in imprt): # when aa.bb.*;
            return False
        imprt = imprt.strip("import ").strip(";").split(".")
        if(self.termVariationMatching(imprt[len(imprt)-1], statement)):
            return True

    def getSeparateImports(self, parsed_lines):
        deleted = parsed_lines["deleted"]

        import_deletes = []
        final_import_deletes = []
        delete_last = 0
        add_last = 0
        import_in_ad_code=dict()
        import_in_del_code =dict()
        idx = 0
        for line in deleted:
            if(not self.findComment(line[1])):
                if("package " not in line[1]):
                    if(line[1].find('import', 0) == 0):
                        import_deletes.append(line[1])
                        delete_last =idx
            idx +=1
        added = parsed_lines["added"]
        final_import_added = []
        import_added = []
        idx=0
        for line in added:
            if(not self.findComment(line[1])):
                if("package " not in line[1]):
                    if(line[1].find('import', 0) == 0):
                        import_added.append(line[1])
                        add_last = idx
            idx +=1
        final_import_added, final_import_deletes = self.onlyDifferentiateImports(import_added,import_deletes,)
        if(len(final_import_deletes)>0):
            for line in deleted[delete_last+1:]:
                if (not self.findComment(line[1])):
                    for imprt in final_import_deletes:
                        if(self.isImportInStatement(imprt, line[1])):
                            import_in_del_code.setdefault(imprt, []).append(line[1])
                            # if(imprt not in import_in_del_code.keys()):
                            #     import_in_del_code[imprt] = [line[1]]
                            # else:
                            #     import_in_del_code[imprt].extend(line[1])

        if (len(final_import_added) > 0):
            for line in added[add_last + 1:]:
                if (not self.findComment(line[1])):
                    for imprt in final_import_added:
                        if (self.isImportInStatement(imprt, line[1])):
                            import_in_ad_code.setdefault(imprt, []).append(line[1])

        # add_imprts = []
        # delete_imports = []

        # del_import = modification.diff.count("-import")
        # ad_import = modification.diff.count("+import")
        # add_pack_count = modification.diff.count("+package")
        # del_pack_count = modification.diff.count("-package")
        # if ((del_import + ad_import + add_pack_count + del_pack_count) > 0):
        #     for imprt in modification.diff.split('\n'):
        #         # add_line_count = modification.diff.count("+\n")
        #         # del_line_count = modification.diff.count("-\n")
        #         # add_slash_count = modification.diff.count("\\+[\s]*//") + modification.diff.count("\\+[\s]*/")
        #         # add_at_count = modification.diff.count("+@")
        #         # del_slash_count = modification.diff.count("-[\s]*//") + modification.diff.count("-[\s]*/")
        #         # del_at_count = modification.diff.count("+@")
        #         # add_todo_count = len(re.findall("\\+[\s]*TODO", modification.diff))  # modification.diff.count("+ *")
        #         # del_todo_count = len(re.findall("-[\s]*TODO", modification.diff))  # modification.diff.count("- *")
        #         # add_star_count = len(re.findall("\\+[\s]*\\*", modification.diff))  # modification.diff.count("+ *")
        #         # del_star_count = len(re.findall("-[\s]*\\*", modification.diff))
        #         if (imprt.find('-import', 0) == 0):
        #             delete_imports.append(imprt)
        #         if (imprt.find('+import', 0) == 0):
        #             add_imprts.append(imprt)
        #         # if (imprt.find('-package', 0) == 0):
        #         #     imprts.append(imprt)
        #         # if (imprt.find('+package', 0) == 0):
        #         #     imprts.append(imprt)

        return (final_import_added, final_import_deletes, import_in_ad_code, import_in_del_code)


    # Modification information extraction that only involved module operaitons
    def changeYamlAnalysis(self, info_path="/mnt/hadoop/vlab/a2aExtraction/",url="commit/"):
        csvfile = open(self.filter_path, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        idx=0
        for row in reader:

            parts = row[0].split("/")
            ID= parts[len(parts)-1]
            OchangeRelation = ChangeRelation()
            OchangeRelation.setId(ID)
            OchangeRelation.setProjectRoort(self.repo_path)
            OchangeRelation.extractYaml(info_path+"/" + OchangeRelation.id + ".yml")
            OchangeRelation.changeInstanceCount()
            OchangeRelation.changeStat()
            OchangeRelation.totalInstances()
            OchangeRelation.saveAnalysisToYaml(info_path + "/" + str(idx+1) + ".yml")
            idx +=1

        csvfile.close()
    def relationInstance(self, ID, repo_path, file_path):
        OchangeRelation_tool = ChangeRelation()
        OchangeRelation_tool.setId(ID)
        OchangeRelation_tool.setProjectRoort(repo_path)
        OchangeRelation_tool.extractYaml(file_path)
        OchangeRelation_tool.changeInstanceCount()
        # OchangeRelation_tool.totalInstances()
        OchangeRelation_tool.printSSCNumbers()
        return OchangeRelation_tool

    def contexts(self, ID, repo_path, file_path):
        OchangeRelation_tool = ChangeRelation()
        OchangeRelation_tool.setId(ID)
        OchangeRelation_tool.setProjectRoort(repo_path)
        OchangeRelation_tool.extractYaml(file_path)
        OchangeRelation_tool.moduleSummary()
        return OchangeRelation_tool

    def extractOperationRuleName(self, validation_path="", save_path=""):
        csvfile = open(self.filter_path, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        fl = open(save_path, 'w')
        csv_write = csv.writer(fl)
        for row in reader:

            parts = row[0].split("/")
            if (row[3] == "False" or row[3] == "FALSE"):
                continue
            ID= parts[len(parts)-1]
            print(ID)
            manual = self.relationInstance(ID, self.repo_path,validation_path + "/" + ID + ".yml")
            op_rule = RuleName()
            op_rule.extractDetailsSCO(manual)
            csv_write.writerow([row[0],','.join(op_rule.op_list), row[2], row[8], row[17],row[7]])
            #TODO-for testing only
            # csv_write.writerow([row[0], ','.join(op_rule.op_list)])
             # print(ID, op_rule.op_list)
        fl.close()
        csvfile.close()

    def directSSCExtarction(self, validation_path="", save_path=""):
        index = 0
        for row in self.commits:
            ID = None
            part = row[0].split(" ")[0]
            ID = part
            if("/" in part):
                parts = part.split("/")
                ID= parts[len(parts)-1]
            print(ID)
            try:
                manual = self.relationInstance(ID, self.repo_path,validation_path + "/" + ID + ".yml")
                manual.moduleSummary()
                if(manual.is_archi==True and manual.sscElementSize()>0):
                    print(row[0])
                    # relation.totalInstances()
                    # row[1] = relation

                    op_rule = RuleName()
                    op_rule.extractDetailsSCO(manual)

                    # csv_write.writerow([row[0],','.join(op_rule.op_list), row[2], row[8], row[17],row[7]])
                    #TODO-for testing only
                    # csv_write.writerow([row[0], ','.join(op_rule.op_list)])
                    # print(ID, op_rule.op_list)
                    ops = op_rule.op_list
                    if("NON_M2M" in ops):
                        ops.remove("NON_M2M")
                    if(len(ops)>0):
                        row[1] = ','.join(op_rule.op_list)
                        mv_c_string = []
                        if (len(manual.moved_classes) > 0):
                            from_cls, to_cls = manual.formattingMovedClass()
                            mv_cls_string = "Moved classes: "
                            for ky in from_cls.keys():
                                mv_cls_string = mv_cls_string + ky + "||" + ",".join(list(from_cls[ky]))
                            to_cls_string = "Moved into: "
                            for ky in to_cls.keys():
                                to_cls_string = to_cls_string + ky + "||" + ",".join(list(to_cls[ky]))

                            mv_c_string.append(mv_cls_string)
                            mv_c_string.append(to_cls_string)
                        mv_m_string = []
                        if (len(manual.moved_methods) > 0):
                            from_cls, to_cls = manual.formattingMovedMethod()
                            mv_cls_string = "Moved method: "
                            for ky in from_cls.keys():
                                mv_cls_string = mv_cls_string + ky + "||" + ",".join(list(from_cls[ky]))
                            to_cls_string = "Moved method into: "
                            for ky in to_cls.keys():
                                to_cls_string = to_cls_string + ky + "||" + ",".join(list(to_cls[ky]))

                            mv_m_string.append(mv_cls_string)
                            mv_m_string.append(to_cls_string)
                        row[Change.MODULE_SUMMARY_INDEX] = [manual.module_summary,mv_c_string, mv_m_string]
                        row[Change.DESIGN_SUMMARY_INDEX] = manual.design_summary
                        self.filtered_commits.append(row)
                        index = index+1
                        self.archi_commit +=1
            except Exception as e:
                print(e)
                pass



    def addCheck(self, content):
        if('ONLY_ADD' in content):
            return True
        if ('MODIFY_NEW_METHOD' in content):
            return True
        if ('MODIFY_NEW_API_METHOD' in content):
            return True
        if ('NEW_MO' in content):
            return True
        if ('MODIFY_CONNECT' in content):
            return True
        if ('MODIFY_API_CONNECT' in content):
            return True
        if ('CLASS_ADD' in content):
            return True
        return False
    def deleteCheck(self, content):
        if('ONLY_DELETE' in content):
            return True
        if ('MODIFY_DELETE_METHOD' in content):
            return True
        if ('MODIFY_DELETE_API_METHOD' in content):
            return True
        if ('DELETE_MO' in content):
            return True
        if ('MODIFY_DISCONNECT' in content):
            return True
        if ('MODIFY_API_DISCONNECT' in content):
            return True
        if ('CLASS_DELETE' in content):
            return True
        return False

    def cross_conn_check(self, c_d_matrix):
        conn = 0
        disconn = 0
        i=0
        add_delete_twist = False
        for row in c_d_matrix:
            conn += row[0]
            disconn += row[1]
            j=0

            for rr in c_d_matrix:
               if(i != j):
                  if(row[0]==1):
                      if(rr[1]==1):
                          add_delete_twist = True
                  if(row[1]==1):
                      if(rr[0]==1):
                          add_delete_twist = True
               j +=1
            i +=1
        return (conn, disconn, add_delete_twist)
    def designGraphUpdate(self, commit_id, summary, type):
        mod_keys = list(summary.keys())
        summary_content = []
        modified_id = "C"+str(self.sudo_id)
        self.commit_identifiers[modified_id] = commit_id
        self.sudo_id +=1
        commit=[modified_id, type, [],[]]
        try:
            for mod_key in mod_keys:
                single_summary = summary[mod_key]
                ob = [[mod_key, single_summary[0]], [list(single_summary[1]), single_summary[2]]]
                summary_content.append(ob)
                commit[2].append(mod_key)
                commit[3].append(single_summary[2])
        except Exception as err:
            print(commit_id)
            print("Issues for instance construction for graph nodes:"+ str(err))

        self.dg.designGraph(commit, summary_content)
    def designUpdate(self,  summary, type):
        index = 0
        if("perfective" in type):
            index = 0
        if ("preventive" in type):
            index = 1
        if ("corrective" in type):
            index = 2
        if ("adaptive" in type):
            index = 3
        mods = summary
        mod_keys = list(mods.keys())
        exist_keys = list(self.design_modules[index].keys())
        for mod_key in mod_keys:
            if (mod_key in exist_keys):
                exist_content = self.design_modules[index][mod_key]
                self.design_modules[index][mod_key] = exist_content + "\n" + mods[mod_key]
            else:
                self.design_modules[index][mod_key] = mods[mod_key]
    def savetoText(self, modules):
        for indx in range(0,4):
            print(Change.classes[indx])
            file = open( "/mnt/hadoop/vlab/jpmsproject/structure_modification/separated/design_summary/"+ Change.classes[indx]+"_design_summary.txt", "w")

            for sample in list(modules[indx].keys()):
                file.write("\n|||||||||" +sample + "|||||||||:\n"+ modules[indx][sample] + '\n')

            file.close()


    def conextAndModuleNo(self, validation_path, csv_write, r_rows):

        for row in r_rows:
            parts = row[0].split("/")
            # if (row[3] == "False" or row[3] == "FALSE"):
            #     continue
            ID= parts[len(parts)-1]
            try:
                manual = self.contexts(ID, self.repo_path,validation_path + "/" + ID + ".yml")
                manual.nonM2MContext()
                mo_num = manual.moduleNumbers()
                self.designUpdate( manual.design_summary, row[3])
                self.designGraphUpdate(ID, manual.summary_for_graph, row[3])
                row.append(' '.join(list(manual.contexts)))
                row.append(mo_num)  # TODO-for testing only
                if(len(manual.cross_modules)>1):
                    row.append("MULTIPLE_CROSS")
                else:
                    row.append("SINGLE_CROSS")
                if("Single" in mo_num):
                    if(self.addCheck(row[1])==True):
                        row.append("ADDITION")
                    else:
                        row.append("NO_ADDITION")
                else:
                    conn, disconn, twist = self.cross_conn_check(manual.c_d_matrix)
                    if(conn>1):
                        row.append("C_MULTIPLE_MOD")
                    else:
                        row.append("C_NO_M")
                if (mo_num == 'Single'):
                    if (self.deleteCheck(row[1]) == True):
                        row.append("DELETION")
                    else:
                        row.append("NO_DELETION")
                else:
                    conn, disconn, twist = self.cross_conn_check(manual.c_d_matrix)
                    if(disconn>1 or twist==True):
                        row.append("TWIST_MULTIPLE_MOD")
                    else:
                        row.append("NO_TWIST")
                methd =''
                if(len(manual.constructors)>0):
                    methd = "CONSTRUCTOR"
                if(len(manual.methods)>0):
                    methd = methd +" " +"METHOD"
                row.append(methd)
                csv_write.writerow(row)
            except Exception as e:
                print(str(e))
                pass
                # csv_write.writerow([row[0], ','.join(op_rule.op_list)])
                # print(ID)
        self.savetoText(self.design_modules)
        self.dg.betterGraphDisplay()
        # self.dg.designGraphDisplay()
    # similar to a2aFilter, This method extracts change relations of the commits on: modules, classes, methods, and imports
    # ----------------------------------------------------------------------------------
    def primarychangeData(self, info_path="/mnt/hadoop/vlab/a2aExtraction/",url="commit/"):
        csvfile = open(self.filter_path, 'r' , encoding="utf8",errors='ignore')
        reader = csv.reader(csvfile, delimiter=',')
        gr = GitRepository(self.repo_path)

        repo = git.Repo(self.repo_path)
        is_tmp_class = False
        is_bug = False
        # test_count = 0
        # only_import_count = 0
        structural_change_count = 0
        for row in reader:
            # if(row[3]=="False" or row[3]=="FALSE"):
            #     continue
            # print(row[0])
            self.total_commit +=1
            is_module_operation = False
            ID = None
            part = row[0].split(" ")[0]
            ID = part
            if("/" in part):
                parts = part.split("/")
                ID= parts[len(parts)-1]
            OchangeRelation = ChangeRelation()
            OchangeRelation.setId(ID)
            self.commit_ids.append(ID)
            commit = gr.get_commit(ID)
            # gr.reset()
            try:
                repo.git.checkout('master')
                gr.checkout(ID)
            except Exception as e:
                print(ID, e)
                pass
            is_bug = self.bugFixDetect(commit.msg)
            if(is_bug):
                self.total_bug +=1
            files = set()
            files_delete = set()
            added = []
            added_stat = {}
            deleted_stat = {}
            deleted = []
            is_delete =False
            types = set()
            tmp_class_impact = set()
            tmp_test_class = set()
            module_delete = set()
            module_add = set()
            module_modified = set()
            module_rename = set()
            class_delete = set()
            class_add = set()
            class_rename = set()
            class_modified = set()
            mo_add_dic = dict()
            mo_delete_dic = dict()
            import_dependency = {}
            unique_jpms = dict()
            all_mdls, all_pkg = self.jpmsModules()
            OchangeRelation.setProjectRoort(self.repo_path)
            OchangeRelation.allModules(list(all_mdls))
            OchangeRelation.allPackages(list(all_pkg))
            OchangeRelation.setModuleNameInFile(self.extractModuleNameFromFile(all_mdls))
            deleted_paths = []
            def onlyModPart(mdl):
                #
                # if("/src/main/java/" in mdl):
                #     return mdl.split("/src/main/java/")[0] + "/src/main/java/"
                # elif("/main/java/" in mdl):
                #     return mdl.split("/main/java/")[0] + "/main/java/"
                # elif("/src/" in mdl):
                #     return mdl.split("/src/")[0] + "/src/"

                if("/src/main/java/" in mdl):
                    return mdl.split("/src/main/java/")[0]
                elif ("/src/main/kotlin/" in mdl):
                    return mdl.split("/src/main/kotlin/")[0]
                elif("/main/java/" in mdl):
                    return mdl.split("/main/java/")[0]
                elif("/src/" in mdl):
                    return mdl.split("/src/")[0]
                else:
                    return mdl

            def onlyClassPart(mdl):

                if("/src/main/java/" in mdl):
                    return mdl.split("/src/main/java/")[1]
                elif ("/src/main/kotlin/" in mdl):
                    return mdl.split("/src/main/kotlin/")[1]
                elif("/main/java/" in mdl):
                    return mdl.split("/main/java/")[1]
                elif("/src/" in mdl):
                    return mdl.split("/src/")[1]
                else:
                    return mdl
            is_archi = False
            for modification in commit.modifications:

                if (self.moduleCheck(modification.filename)): #only module-info.java file

                    fil_path = self.existedPath(modification.new_path, modification.old_path)

                    # ----------------------------------------------------------------------------------
                    # read and parse the content of the module file
                    # ----------------------------------------------------------------------------------
                    # self.moduleContentHashing(modification.source_code_before, fil_path, module_paths, module_codes)

                    # TODO: need to extract all ops added--done
                    # TODO: need to extract all ops deleted --done

                    if(self.checkTest(fil_path)):
                        Omod = None
                        new_mod = False
                        jpms_name = onlyModPart(fil_path.replace(self.repo_path + "/", ""))
                        allnames = unique_jpms.keys()
                        if(jpms_name in allnames):
                            Omod = unique_jpms[jpms_name]
                        else:
                            Omod = JPMSMod()

                            Omod.setName(jpms_name)
                            new_mod=True
                        has_live_module=True
                        is_module_operation = False
                        # Do not consider File rename and modification with comments as module change operations
                        only_add = False
                        only_delete = False
                        if(modification.change_type.name is commit_type[0]): # ADD
                            only_add = True
                            module_add.add(modification.new_path)
                            Omod.setChangeType(commit_type[0])
                        if (modification.change_type.name is commit_type[2]): # DELETE
                            only_delete = True
                            module_delete.add(modification.old_path)
                            Omod.setChangeType(commit_type[2])
                        if (modification.change_type.name is commit_type[3]): # MODIFY
                            module_rename.add(modification.new_path)
                            Omod.setChangeType(commit_type[3])

                        parsed_lines = modification.diff_parsed#modification.diff_parsed
                        tmp_delete = []
                        tmp_add = []
                        #----------------------------------------------------------------------------------
                        # separate added and deleted lines (MO operations).
                        # Need to handle comment like: //, *, /* within the prased module-info.java content
                        # ----------------------------------------------------------------------------------
                        self.parseMO(parsed_lines, modification, added_stat, tmp_add, deleted_stat, tmp_delete,files_delete, files, is_module_operation)
                        # ----------------------------------------------------------------------------------
                        # store the added or deleted mo operations (exports, requires) into dictionary and list
                        # ----------------------------------------------------------------------------------
                        if(len(tmp_delete)>0 and only_add==False):
                            is_delete = True
                            is_module_operation = True
                            mo_delete_dic[fil_path] = tmp_delete
                            Omod.opsDeleteInModule(tmp_delete)
                            deleted.extend(tmp_delete)
                        if (len(tmp_add) and only_delete == False):
                            mo_add_dic[fil_path] = tmp_add
                            added.extend(tmp_add)
                            is_module_operation = True
                            Omod.opsAddInModule(tmp_add)
                        if(only_add or only_delete):
                            is_module_operation=True
                        # ----------------------------------------------------------------------------------
                        # store the modified file name
                        # ----------------------------------------------------------------------------------
                        if ((len(tmp_delete) + len(tmp_add)) > 0):
                            is_archi = True
                        if(is_module_operation):
                            module_modified.add(fil_path)
                            is_archi = True
                        if(modification.change_type.name != "RENAME" and modification.change_type.name != "MODIFY"):
                            is_module_operation = True
                        # OchangeRelation.addModule(Omod)

                        unique_jpms[jpms_name] = Omod


                    else:
                        has_test = True
                elif(self.fileCheck(modification.filename)):
                    # ensure all modification checked

                    fil_path = self.existedPath(modification.new_path, modification.old_path)
                    print(fil_path)
                    if(self.checkTest(fil_path)):
                        module_name = OchangeRelation.findModlOfCls(fil_path)
                        if(module_name != None):
                            module_name = onlyModPart(module_name)

                        Omodule = None
                        new_mod = False
                        allnames = unique_jpms.keys()
                        already_exists = False
                        if (module_name is None):
                            module_name = onlyModPart(fil_path.replace(self.repo_path + "/", ""))

                        if (module_name != None):
                            for existname in list(allnames):
                                if (module_name == existname):
                                    Omodule = unique_jpms[module_name]
                                    already_exists = True
                                    break
                        if(not already_exists):
                            Omodule = JPMSMod()
                            Omodule.setName(module_name)
                            Omodule.setType("NATIV")
                            new_mod = True
                        if (is_bug):
                            self.bug_cls.add(fil_path)
                        if (modification.change_type.name is commit_type[0]): # ADD operation
                            class_add.add(modification.new_path)
                            Oclass = JPMSClass()
                            Oclass.setName(onlyClassPart(modification.new_path))
                            imprts = self.getIncludeDependency(modification)
                            Oclass.addImport(imprts)
                            print(
                                "---------------------------------------------from added class-----------------------")

                            added_mthds, deleted_mthds = self.experimentalExtractMethods(gr, modification,
                                                                                         commit.committer_date)
                            Oclass.addAddedMethod(added_mthds)
                            Oclass.addDeleteMethod(deleted_mthds)
                            is_archi = True
                            #TODO: need to extract all imports for the class -- done
                            Omodule.addedClass(Oclass)

                        if (modification.change_type.name is commit_type[2]): # DELETE operation
                            class_delete.add(modification.old_path)
                            Oclass = JPMSClass()
                            Oclass.setName(onlyClassPart(modification.old_path))
                            imprts = self.getIncludeDependency(modification)
                            Oclass.deleteImport(imprts)
                            # TODO: need to extract all imports for the class -- done

                            print("---------------------------------------------from deleted class-----------------------")
                            added_mthds, deleted_mthds = self.experimentalExtractMethods(gr, modification,
                                                                                         commit.committer_date)
                            is_archi = True
                            Oclass.addAddedMethod(added_mthds)
                            Oclass.addDeleteMethod(deleted_mthds)

                            Omodule.deletedClass(Oclass)
                            deleted_paths.append(self.getRelativePackage(modification.old_path))
                        if (modification.change_type.name is commit_type[3]): #RENAME operation
                            class_rename.add(onlyClassPart(modification.new_path))
                        # ----------------------------------------------------------------------------------
                        # This determine whether a file modification is aligned within the modified modules (context or non-context)
                        #There are three possible directory of a module: src/module, src/main/java/, src/abc../main/java

                        if(modification.new_path != None):
                            # ----------------------------------------------------------------------------------
                            # determine whether a file modifications are only import change or not. Does not contain modification of other statements
                            # ----------------------------------------------------------------------------------
                            if (self.onlyImport(modification, gr) == False):
                                only_import = False

                        #types.append(modification.change_type.name)
                        #print(fil_path)
                        if (modification.change_type.name is commit_type[1] or modification.change_type.name is commit_type[3]): # extract import statement from renamed or modified file
                            # if(self.similarImportChange(modification.diff_parsed)):
                            #     continue


                            if(modification.change_type.name is commit_type[1]): # MODIFY operation
                                class_modified.add(fil_path)
                            # need to handle cases where import != in the first place
                            # imprts = self.getIncludeDependency(modification)
                            add_imprts, del_imports, import_in_ad, import_in_del = self.getSeparateImports(modification.diff_parsed)
                            Oclass = JPMSClass()
                            Oclass.setName(onlyClassPart(fil_path))
                            if(len(add_imprts+del_imports)>0):
                                is_archi=True
                                # ----------------------------------------------------------------------------------
                                # store file name having import change
                                # ----------------------------------------------------------------------------------
                                # import_dependency[fil_path] = imprts
                                Oclass.addImport(add_imprts)
                                Oclass.deleteImport(del_imports)
                                Oclass.imprtInAddedCode(import_in_ad)
                                Oclass.imprtInDeletedCode(import_in_del)
                                added_mthds, deleted_mthds = self.experimentalExtractMethods(gr,modification, commit.committer_date)
                                Oclass.addAddedMethod(added_mthds)
                                Oclass.addDeleteMethod(deleted_mthds)
                                self.commitOP(modification, types, tmp_class_impact)
                            # self.extractModifiedMethods(gr,modification,commit.committer_date)
                            # TODO: need to extract added methods -- all done
                            # TODO: need to extract deleted methods
                            # TODO: need to extract added imports
                            # TODO: need to extract deleted imports
                            # TODO: need to extract added code with import change
                            # TODO: need to extract deleted code with import change -- all done
                            Omodule.modifiedClass(Oclass)
                        unique_jpms[module_name] = Omodule
                    else:
                        has_test = True
                        tmp_test_class.add(fil_path)
            for ky in unique_jpms.keys():
                OchangeRelation.addModule(unique_jpms.get(ky))
            if(len(deleted_paths)>0):
                OchangeRelation.extendsPacDirs(deleted_paths)
            OchangeRelation.findMovingMethod()
            if(OchangeRelation.getArchiPrediction()==True and is_archi==True):
                self.commits.append([row[0],OchangeRelation, row[2],"", "","",""])
                self.change_relations.append(OchangeRelation)

    # def methodMoveAnalysis(self, changerelation):

    def changeRelationAnalyze(self,info_path="a2aExtraction/"):
        import yaml
        # TODO: need to extract all connected modules
        # TODO: need to extract all disconnected modules
        for relation in self.change_relations:
            relation.setProjectRoort(self.repo_path)
            relation.analyze()
            relation.saveAnalysisToYaml(info_path+"/" + relation.id + ".yml")
            # add_data = []
            # for jpmsmod in relation.modules:
            #
            #     uses_data = []
            #     for clss in jpmsmod.added_classes:
            #
            #         uses_data.append({clss.full_name:clss.import_added})
            #     add_data.append({'added':{jpmsmod.full_name: uses_data}})
            #     with open('data.yml', 'a') as outfile:
            #         yaml.dump(add_data, outfile, default_flow_style=False)


    def commitedChangeRelationAnalyze(self,info_path="a2aExtraction/"):
        import yaml
        # TODO: need to extract all connected modules
        # TODO: need to extract all disconnected modules

        for row in self.commits:
            relation = row[1]
            relation.setProjectRoort(self.repo_path)
            relation.analyze()
            relation.changeInstanceCount()
            # if(relation.is_archi==True):
            #     print(row[0])
            #     relation.totalInstances()
            #     row[1] = relation
            #     self.filtered_commits.append(row)
            relation.saveAnalysisToYaml(info_path+"/" + relation.id + ".yml")
            # self.archi_commit+=1


    def findModuleFor(self, com_state, class_dir):
        mod_name = None
        to_search = class_dir.split("/src/")[0]+"/src/"
        to_search2 = class_dir.split("/main/java/")[0] + "/main/java/"
        to_search3 = class_dir.split("/src/main/java/")[0] + "/src/main/java/"
        to_search4 = class_dir.split("/src/")[0] + "/"
        # print(to_search)
        for mdl in com_state.jpms:
            if(to_search in mdl or to_search2 in mdl or to_search3 in mdl or to_search4 in mdl):
                return mdl


        return mod_name
    def putHotjpms(self, jpm):
        if jpm not in self.jpmshot.keys():
            self.jpmshot[jpm] = 1
        else:
            self.jpmshot[jpm] += 1

    def putHotcls(self, cls):
        if cls not in self.classhot.keys():
            self.classhot[cls] = 1
        else:
            self.classhot[cls] += 1

    def getJpmsInfo(self):
        hotspot = []
        keys = self.jpmshot.keys()
        lngth = len(keys)
        for ky in keys:
            val = self.jpmshot.get(ky)
            if((val/len(self.commits_state))>=0.10):
                hotspot.append(ky)
        return [lngth, len(hotspot)]

    def getClassesInfo(self):
        hotspot = []
        keys = self.classhot.keys()
        lngth = len(keys)
        for ky in keys:
            val = self.classhot.get(ky)
            if ((val / len(self.commits_state)) >= 0.10):
                hotspot.append(ky)
        return [lngth, len(hotspot)]

    def storeInChangeType(self, typeO,com_state):
        typeO.setTotal(1)
        for md in com_state.module_add:
            typeO.putJpms(md)
            self.putHotjpms(md)
        for md in com_state.module_delete:
            typeO.putJpms(md)
            self.putHotjpms(md)
        for md in com_state.module_modify:
            typeO.putJpms(md)
            self.putHotjpms(md)
        for md in com_state.module_rename:
            typeO.putJpms(md)
            self.putHotjpms(md)
        for cls in com_state.class_add:
            typeO.putClasses(cls)
            self.putHotcls(cls)
        for cls in com_state.class_delete:
            typeO.putClasses(cls)
            self.putHotcls(cls)
        for cls in com_state.class_rename:
            typeO.putClasses(cls)
            self.putHotcls(cls)
        # print(com_state.a2aClass)
        for cls in com_state.a2aClass:
            typeO.putClasses(cls)
            self.putHotcls(cls)

    # claculate statistics of each category
    def a2aCategory(self):

        for com_state in self.commits_state:
            cats = self.commit_cat[com_state.id]
            if ("perfective" in cats):
                # print(word)
                self.storeInChangeType(self.perfectiveO, com_state)
            if ("corrective" in cats):
                self.storeInChangeType(self.correctiveO, com_state)
            if ("adaptive" in cats):
                self.storeInChangeType(self.adaptiveO, com_state)
            if ("preventive" in cats):
                self.storeInChangeType(self.preventiveO, com_state)


    # claculate statistics of each category
    def categoryStat(self):
        return [self.project_name, self.perfectiveO.a2aGist(), self.preventiveO.a2aGist(), self.correctiveO.a2aGist(), self.adaptiveO.a2aGist(), [self.getJpmsInfo(), self.getClassesInfo()]]