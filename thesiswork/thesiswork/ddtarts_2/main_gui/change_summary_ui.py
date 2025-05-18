from tkinter import *
from ChangeAnnotation.experiment_change_extraction import *
from preproces_mod.preprocess import Preprocess,DataSave
from category_analysis.tangled_category import TangleCategory
from category_analysis import model
from category_analysis.category_mod import Category
import threading



import tkinter.scrolledtext as scrolledtext
class CSummaryUI:
    def __init__(self, master=None):
        self.master = master
    def openNewWindow(self):
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self.master)

        # sets the title of the
        # Toplevel widget
        newWindow.title("Change summary generation window")

        # sets the geometry of toplevel
        newWindow.geometry("800x600")

        # A Label widget to show in toplevel
        lblFile = Label(newWindow,
              text="Commit file path")
        lblFile.place(x=200, y=100)
        # lblFile.pack()
        fileInptArea = Entry(newWindow, width=30)
        fileInptArea.place(x=350, y=100)

        lblsscDir = Label(newWindow,
              text="SSC save directory")
        lblsscDir.place(x=200, y=150)
        # lblFile.pack()
        dirInptArea = Entry(newWindow, width=30)
        dirInptArea.place(x=350, y=150)

        txt = scrolledtext.ScrolledText(newWindow, undo=True, width = 60, height=10)

        txt['font'] = ('consolas', '10')
        txt.place(x=200, y=250)
        txt.insert(INSERT, "Release note will go here\n with bug fixing and so on")


        generateButton = Button(newWindow, anchor="w", text="Generate change Summary",
                                     command=None, height=2, width=30)
        generateButton.place(x=200, y=450)
        # fileInptArea.pack()

class DRleaseNoteUI:
    TYPE_INDEX=3
    # COMMIT_MSG_INDEX=2 azure
    # For speedment it is COMMIT_MSG_INDEX 11
    COMMIT_MSG_INDEX = 2
    PREDICTED_TYPE_INDEX = 3
    MSG_INDEX_AFTER_STEMMING = 4
    SSC_OP_INDEX = 1
    def __init__(self, summary=0,master=None):
        self.master = master
        self.fileInptArea=None
        self.dirInptArea= None
        self.scrollText = None
        self.repoDirInputArea = None
        self.summary_type = summary # 0 means release summary and 1 means commit summary
        self.repositoryChkBtn = None
        self.nouns = []
        self.adjectives = []
        self.from_repo = IntVar()
        self.from_extracted_info = IntVar()
        self.is_from_repo = 1
    def openNewWindow(self):
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self.master)

        # sets the title of the
        # Toplevel widget
        newWindow.title("Change summary generation window")

        # sets the geometry of toplevel
        newWindow.geometry("1000x800")


        self.repositoryChkBtn = Checkbutton(newWindow, text='From git codebase revisions', variable=self.from_repo, onvalue=1, offvalue=0, command=self.checkedOption)
        self.repositoryChkBtn.place(x=200, y=50)
        self.repositoryChkBtn.select()
        # A Label widget to show in toplevel
        lblFile = Label(newWindow,
              text="Commit file path")
        lblFile.place(x=200, y=100)
        # lblFile.pack()
        self.fileInptArea = Entry(newWindow, width=30) #/mnt/hadoop/vlab/jpmsproject/structure_modification/hiber_search_correct.csv
        self.fileInptArea.place(x=350, y=100)
        self.fileInptArea.insert(0, "/mnt/hadoop/vlab/jpmsproject/structure_modification/projects_input_for_ddarts/hiber_search_input_ddarts.csv")
        lblsscDir = Label(newWindow,
              text="SSC save directory")
        lblsscDir.place(x=200, y=150)
        # lblFile.pack()
        self.dirInptArea = Entry(newWindow, width=30)#/mnt/hadoop/vlab/jpmschange_info/ddarts_experiment
        self.dirInptArea.place(x=350, y=150)
        self.dirInptArea.insert(0,"/mnt/hadoop/vlab/jpmschange_info/ddarts_experiment")
        lblTag = Label(newWindow,
              text="Release Tag")
        lblTag.place(x=200, y=200)
        # lblFile.pack()
        self.tagInptArea = Entry(newWindow, width=30)
        self.tagInptArea.place(x=350, y=200)
        self.tagInptArea.configure(state=DISABLED)
        lblTimeline = Label(newWindow,
              text="Release Timeline")
        lblTimeline.place(x=200, y=250)
        # lblFile.pack()
        timeInptArea = Entry(newWindow, width=30)
        timeInptArea.place(x=350, y=250)
        timeInptArea.configure(state=DISABLED)

        lblTimeline = Label(newWindow,
              text="Local repo directory")
        lblTimeline.place(x=200, y=300)
        # lblFile.pack()
        self.repoDirInputArea = Entry(newWindow, width=30)#/mnt/hadoop/vlab/experiment_repo/hibernate-search
        self.repoDirInputArea.place(x=350, y=300)
        self.repoDirInputArea.insert(0,"/mnt/hadoop/vlab/experiment_repo/hibernate-search")
        # txtArea = Text(newWindow, width = 60, height=10)
        # txtArea.place(x=200, y=300)
        # # txtScroll = Scrollbar(newWindow)
        # # txtScroll.pack(side=RIGHT, fill=Y)
        # # txtScroll.configure(command=txtArea.yview)
        # txtArea.grid(row=300, column=200,sticky="nsew", padx=2, pady=2)
        #
        # # create a Scrollbar and associate it with txt
        # txtScroll = Scrollbar(newWindow, command=txtArea.yview)
        # txtScroll.grid(row=0, column=0, sticky='nsew')
        # txtArea['yscrollcommand'] = txtScroll.set
        self.scrollText = scrolledtext.ScrolledText(newWindow, undo=True, width = 100, height=12)

        self.scrollText['font'] = ('consolas', '10')
        self.scrollText.place(x=200, y=350)
        self.scrollText.insert(INSERT, "Summary note will go here\n with feature add \n bug fixing \n reafactoring \n adaptive")
        # txt.pack(expand=True, fill='both')
        summary_tex="Generate release change logs"
        if(self.summary_type == 1):
            summary_tex ="Generate commit summaries note"

        generateButton = Button(newWindow, anchor="w", text=summary_tex,
                                     command=self.startProcessing, height=2, width=30)
        generateButton.place(x=200, y=550)
        # fileInptArea.pack()
    def checkedOption(self):

        if (self.from_repo.get() == 1):
            self.is_from_repo = 1
            print("----- from repo")
            self.repoDirInputArea.configure(state=NORMAL)
        elif(self.from_repo.get() == 0):
            print("---------- not from repo")
            self.is_from_repo = 0
            self.repoDirInputArea.configure(state=DISABLED)
    def startProcessing(self):
        self.scrollText.delete(1.0,END)
        repo_path = self.repoDirInputArea.get()
        filepath = self.fileInptArea.get()
        savepath = self.dirInptArea.get()
        self.scrollText.insert(INSERT, filepath)
        self.scrollText.insert(INSERT, savepath)
        self.scrollText.insert(INSERT, "\nPlease wait. Processing...............")
        # self.executeAllPhases(filepath, repo_path, savepath)
        # self.testExecution(filepath, repo_path, savepath)
        ddarts_thread =None
        if(self.is_from_repo==1):
            ddarts_thread= threading.Thread(target=self.threadFunction, args=(filepath, repo_path, savepath,))
        elif(self.is_from_repo==0):
            ddarts_thread = threading.Thread(target=self.testThreadFunction, args=(filepath, repo_path, savepath,))

        ddarts_thread.start()
    def testThreadFunction(self,filepath, repo_path, savepath):
        self.testExecution(filepath, repo_path, savepath)
    def threadFunction(self,filepath, repo_path, savepath):
        self.executeAllPhases(filepath, repo_path, savepath)

    def executeAllPhases(self,commit_path, repo_local, save_path):
        import time
        start_time = time.clock()
        detected_commits = self.detectDIS(commit_path, repo_local, save_path)
        print(time.clock() - start_time, " seconds")
        predicted_groups = self.changeGroupDIS(detected_commits)
        generated_content = self.generateEachSummary(save_path, predicted_groups)
        if (self.summary_type == 1):
            self.generateCommitSummary(generated_content, save_path,DRleaseNoteUI.SSC_OP_INDEX, DRleaseNoteUI.MSG_INDEX_AFTER_STEMMING)
        else:
            self.generateReleaseSummary(generated_content, save_path,DRleaseNoteUI.SSC_OP_INDEX, DRleaseNoteUI.MSG_INDEX_AFTER_STEMMING)
        print(time.clock() - start_time, " seconds")

    def testExecution(self,commit_path, repo_local, save_path):
        import time
        start_time = time.clock()
        detected_commits = self.testDetectDIS(commit_path, repo_local, save_path)
        predicted_groups = self.changeGroupDIS(detected_commits)
        generated_content = self.generateEachSummary(save_path, predicted_groups)
        if(self.summary_type==1):
            self.generateCommitSummary(generated_content, save_path,DRleaseNoteUI.SSC_OP_INDEX, DRleaseNoteUI.MSG_INDEX_AFTER_STEMMING) # For speedment it is COMMIT_MSG_INDEX 11

        else:
            self.generateReleaseSummary(generated_content, save_path,DRleaseNoteUI.SSC_OP_INDEX, DRleaseNoteUI.MSG_INDEX_AFTER_STEMMING)
        print(time.clock() - start_time, " seconds")
        # nount = sorted(self.nouns, key=len, reverse=True)
        # adjectivet = sorted(self.adjectives, key=len, reverse=True)
        # for tok in adjectivet:
        #     print(tok)
        # print("-----------nouns---------")
        # for tok in nount:
        #     print(tok)


    def testDetectDIS(self, commit_path, repo_local, save_path):

        annotation = PrimaryChange(repo_path=repo_local, filter_path=commit_path, save_path="",
                                   project_name="")
        # annotation.primarychangeData(save_path)
        self.scrollText.delete(1.0, END)
        self.scrollText.insert(INSERT, "\nTotal commit "+ str(annotation.total_commit))
        # annotation.commitedChangeRelationAnalyze(save_path) #97b0d008c133944f92714e8c54edd495efbccfa3, 6f69e2f17e0f2abf1357a6e88146c271a440bb5e, 8fab357e6265af53c4537a90ddadb84bb7159862
        #TODO - need a different method to first predict whether its an architectural change or not
        preprocs = Preprocess(commit_path,
                              "--")
        preprocs.readCsvByColumnExtension()
        annotation.commits = preprocs.content
        annotation.directSSCExtarction(validation_path=save_path)
        self.scrollText.insert(INSERT, "\nArchitectural commits " + str(annotation.archi_commit))
        return annotation.filtered_commits

    def detectDIS(self, commit_path, repo_local, save_path):
        annotation = PrimaryChange(repo_path=repo_local, filter_path=commit_path, save_path="",
                                   project_name="")
        annotation.primarychangeData(save_path)
        self.scrollText.delete(1.0, END)
        self.scrollText.insert(INSERT, "\nTotal commit "+ str(annotation.total_commit))
        annotation.commitedChangeRelationAnalyze(save_path) #97b0d008c133944f92714e8c54edd495efbccfa3, 6f69e2f17e0f2abf1357a6e88146c271a440bb5e, 8fab357e6265af53c4537a90ddadb84bb7159862
        #TODO - need a different method to first predict whether its an architectural change or not
        annotation.directSSCExtarction(validation_path=save_path)
        self.scrollText.insert(INSERT, "\nArchitectural commits " + str(annotation.archi_commit))
        return annotation.filtered_commits

    def changeGroupDIS(self, commits_content):
        preprocs = Preprocess("",
                              "")
        preprocs.content = commits_content
        preprocs.correctStemmingWithCode(content_indx=DRleaseNoteUI.COMMIT_MSG_INDEX, retain_index=DRleaseNoteUI.MSG_INDEX_AFTER_STEMMING)  # parse words with code element
        catg = TangleCategory(preprocs.content)
        my_path = os.path.abspath(os.path.dirname(__file__))
        lib_name = Preprocess.textFile(os.path.join(my_path,"../resource/api_name.txt"))
        catg.libraryList(lib_name)
        mod = model.Model(os.path.join(my_path,"../resource/expanded_weight.csv"))
        mod.readModel()
        catg.assignModel(mod.weight)
        mod = model.Model(os.path.join(my_path,"../resource/balanced_op_2022.csv"))
        mod.readModel()
        catg.assignOperationModel(mod.weight)

        #TODO -  need a different method that returns predicted change types
        catg.combinedPredict(text_indx=DRleaseNoteUI.COMMIT_MSG_INDEX, retain_index=DRleaseNoteUI.MSG_INDEX_AFTER_STEMMING, cat_indx=DRleaseNoteUI.TYPE_INDEX, op_indx=DRleaseNoteUI.SSC_OP_INDEX, threshold=.25)
        return  catg.content

    def generateEachSummary(self, save_path, commits_content):
        catg = Category(commits_content)
        catg.separatePredictCat(DRleaseNoteUI.TYPE_INDEX)
        catg.separateCatObjects()
        #TODO-need a different
        catg.loadTrainedSSCWordMap()
        #TODO-need a different method to generated based on the predicteed change one
        catg.designMessageGeneration(save_path, 1)
        return catg

    def generateCommitSummary(self, categorical_message, save_path,op_index, msg_index):
        plain_message = ""
        summaries = []
        for processed_commit in categorical_message.content:
            committed_change = ModuleChange("General")
            single_msg = ""
            commit_msg = "\n"+ processed_commit[0] +"\n"+"--------------------" +"\n"
            commit_msg = commit_msg+ "Commit title: " + "\n" + Preprocess.onlyTitle(processed_commit[msg_index]) + "\n"
            change_type = processed_commit[DRleaseNoteUI.TYPE_INDEX]
            # single_msg = ",".join(ast.literal_eval(change_type))
            change_info = ""
            msg_part = committed_change.msgPartExtraction(processed_commit,msg_index)
            has_conn, has_disconn, change_content = committed_change.generateContentForCommit(processed_commit, msg_index, op_index)
            self.nouns.extend(committed_change.nouns)
            self.adjectives.extend(committed_change.adjectives)
            if(has_conn):
                if ("perfective" in change_type):
                    # print(word)
                    change_info = "Pefective "
                    single_msg = single_msg + " modified or introduced " + msg_part

            if ("corrective" in change_type):
                change_info = change_info+" ,corrective "
                single_msg = single_msg + " bug fixing " + msg_part
            if ("adaptive" in change_type):
                change_info = change_info + " ,adaptive "
                single_msg = single_msg + " adapted or migrated " + msg_part
            if(has_disconn):
                if ("preventive" in change_type):
                    change_info = change_info + " ,preventive "
                    single_msg = single_msg + " restructured " + msg_part
            summaries.append([processed_commit[0],processed_commit[msg_index] , change_info+ +":"+single_msg+ " "+change_content])
            single_msg =commit_msg + change_info+":"+ single_msg+ " "+change_content

            plain_message = plain_message + single_msg + "\n<------------------------------------------------>"
        DataSave(save_path+"/commited_summary.csv", summaries).plainSaveCSV()

        self.scrollText.delete(1.0, END)
        self.scrollText.insert(INSERT, plain_message)
        # DataSave("", "").saveLinesToFile(save_path + "/"+categorical_message.perfective.type, categorical_message.perfective.noun_phrases)
        # DataSave("", "").saveLinesToFile(save_path + "/"+categorical_message.corrective.type, categorical_message.corrective.noun_phrases)
        # DataSave("", "").saveLinesToFile(save_path + "/"+categorical_message.adaptive.type, categorical_message.adaptive.noun_phrases)

        DataSave("","").plainTextSave(save_path+"/commit_summary",plain_message)


    def generateReleaseSummary(self, categorical_message, save_path,op_index, msg_index):

        plain_message = "-----Perfective------:"
        for processed_commit in categorical_message.perfective.samples:
            perf_control, msg = categorical_message.perfective.generatePerfectiveSentence(processed_commit,msg_index, op_index)
            if(perf_control):
                if(msg != ""):
                    plain_message = plain_message + "\n -- "+ msg
        plain_message = plain_message + "\n\n-----Corrective-----:"
        for processed_commit in categorical_message.corrective.samples:
            control, msg = categorical_message.corrective.generateCorrectiveSentence(processed_commit, msg_index, op_index)
            if (msg != ""):
                plain_message = plain_message + "\n -- " + msg
        plain_message = plain_message + "\n\n-----Preventive------:"

        for processed_commit in categorical_message.preventive.samples:
            prevent_control, msg = categorical_message.preventive.generatePreventiveSentence(processed_commit, msg_index, op_index)
            if (prevent_control):
                if (msg != ""):
                    plain_message = plain_message + "\n -- " + msg

        plain_message = plain_message + "\n\n-------Adaptive------:"

        for processed_commit in categorical_message.adaptive.samples:
            control,msg = categorical_message.adaptive.generateAdaptiveSentence(processed_commit, msg_index, op_index)
            if (msg != ""):
                plain_message = plain_message + "\n -- " + msg
        self.scrollText.delete(1.0, END)
        self.scrollText.insert(INSERT, plain_message)
        DataSave("", "").saveLinesToFile(save_path + "/"+categorical_message.perfective.type, categorical_message.perfective.noun_phrases)
        DataSave("", "").saveLinesToFile(save_path + "/"+categorical_message.corrective.type, categorical_message.corrective.noun_phrases)
        DataSave("", "").saveLinesToFile(save_path + "/"+categorical_message.adaptive.type, categorical_message.adaptive.noun_phrases)

        DataSave("","").plainTextSave(save_path+"/release_logs",plain_message)

    # def generateReleaseSummary(self, categorical_message, save_path,op_index, msg_index):
    #     def components(mod_summary, d_summary):
    #         summary = ''
    #         mods = ''
    #         any_conn = False
    #         any_disconn = True
    #         for ky in mod_summary.keys():
    #             mod_list, cls_list, mthd_list, has_non, has_conn, has_disconn, added, deleted, modified = mod_summary[ky]
    #             any_conn = has_conn
    #             any_disconn = has_disconn
    #             single_content = ky
    #             ads = list(added)
    #             dels = list(deleted)
    #             modifies = list(modified)
    #             involved_classes = ""
    #             if(len(ads)>0):
    #                 involved_classes = involved_classes + "added:" + ",".join(ads)
    #             if(len(dels)>0):
    #                 involved_classes = involved_classes + "|| deleted:" + ",".join(dels)
    #             if(len(modifies)):
    #                 involved_classes = involved_classes + "|| modified:" + ",".join(modifies)
    #             single_content =single_content+"-->" +involved_classes + "-->"+",".join(list(mod_list))
    #             if(len(list(cls_list))>0):
    #                 single_content = single_content + "|| class: "+",".join(list(cls_list))
    #             if(len(list(mthd_list))>0):
    #                 single_content = single_content+ "|| method:" + ",".join(list(mthd_list))
    #             summary = single_content + ";" + summary
    #             mods = ky+","+mods
    #         print(summary)
    #         return (mods, summary, any_conn, any_disconn)
    #
    #     plain_message = "Perfective:"
    #     for processed_commit in categorical_message.perfective.samples:
    #         mods, summary, has_conn, has_disconn = components(processed_commit[5], None)
    #         if(has_conn):
    #            plain_message = plain_message+ "\n -- "+Preprocess.onlyTitle(processed_commit[4]) +";" +processed_commit[msg_index] + " in "+ mods+ " <=>" + processed_commit[op_index].lower()+ " <=>" + summary
    #     plain_message = plain_message+ "\n\nCorrective:"
    #     for processed_commit in categorical_message.corrective.samples:
    #         mods, summary, has_conn, has_disconn = components(processed_commit[5], None)
    #         plain_message = plain_message+ "\n -- "+Preprocess.onlyTitle(processed_commit[4]) +";"+ processed_commit[msg_index]+ " in "+ mods+" <=>" + processed_commit[op_index].lower() + " <=>" + summary
    #     plain_message = plain_message + "\n\nPreventive:"
    #     for processed_commit in categorical_message.preventive.samples:
    #         mods, summary, has_conn, has_disconn = components(processed_commit[5], None)
    #         if(has_disconn):
    #             plain_message = plain_message+ "\n -- "+Preprocess.onlyTitle(processed_commit[4]) +";"+ processed_commit[msg_index]+" of "+ mods+ " <=>" + processed_commit[op_index].lower() + " <=>"+ summary
    #     plain_message = plain_message + "\n\nAdaptive:"
    #     for processed_commit in categorical_message.adaptive.samples:
    #         mods, summary , has_conn, has_disconn= components(processed_commit[5], None)
    #         plain_message = plain_message+ "\n -- "+Preprocess.onlyTitle(processed_commit[4]) +";"+ processed_commit[msg_index]+ " for "+ mods+ " <=>" + processed_commit[op_index].lower() + " <=>" + summary
    #     self.scrollText.delete(1.0, END)
    #     self.scrollText.insert(INSERT, plain_message)
    #     DataSave("","").plainTextSave(save_path+"/release_logs",plain_message)

