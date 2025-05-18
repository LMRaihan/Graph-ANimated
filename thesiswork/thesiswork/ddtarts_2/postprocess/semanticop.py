from enum import Enum
from preproces_mod.codechange import *
class SemanticOP(Enum):
    ONLY_ADD=0 #TODO- contain added class
    ONLY_DELETE=1 #TODO- contain dleted class
    ONLY_MODIFY=2 #TODO- contain modified class
    NON_M2M=6
    MODIFY_NEW_METHOD=3 # TODO- only method added in a class, does not contain deleted method
    MODIFY_DELETE_METHOD=4 # TODO- only method deleted in a class, does not contain added method
    ADD_DELETE_MTHD_SAME_CLASS=7 # TODO- contain method add deletetion in a same class
    MODIFY_NEW_API_METHOD = 10  # TODO- only method added in a class, does not contain deleted method
    MODIFY_DELETE_API_METHOD = 11  # TODO- only method deleted in a class, does not contain added method
    ADD_DELETE_API_MTHD_SAME_CLASS = 12  # TODO- contain method add deletetion in a same class
    NEW_MO=5 # TODO- added module
    MODIFY_MO = 8 # TODO- modification of MO file
    MODIFY_NO_METHOD = 9
    MODIFY_CONNECT = 13
    MODIFY_DISCONNECT = 14
    MODIFY_API_CONNECT = 20
    MODIFY_API_DISCONNECT = 21
    CLASS_ADD = 15
    CLASS_DELETE=16
    DELETE_MO = 17
    MO_CONNECT=18
    MO_DISCONNECT=19
    CLASS_MOVE = 22
    METHOD_MOVE =23
    CONSTRUCTOR_MODIFY = 24
    #TODO-- Non m22m might need later for association rule analysis



class OperationRule:

    def __init__(self):
        self.op_list = set()


    def determineOnlyAdd(self):
        self.op_list.add(SemanticOP.ONLY_ADD)
    def determineOnlyDelete(self):
        self.op_list.add(SemanticOP.ONLY_DELETE)
    def determineOnlyModify(self):
        self.op_list.add(SemanticOP.ONLY_MODIFY)
    def determineNewMethod(self):
        self.op_list.add(SemanticOP.MODIFY_NEW_METHOD)
    def determineDeleteMethod(self):
        self.op_list.add(SemanticOP.MODIFY_DELETE_METHOD)
    def determineNewApiMethod(self):
        self.op_list.add(SemanticOP.MODIFY_NEW_API_METHOD)
    def determineDeleteApiMethod(self):
        self.op_list.add(SemanticOP.MODIFY_DELETE_API_METHOD)
    def determineAddDeleteApiMthd(self):
        self.op_list.add(SemanticOP.ADD_DELETE_API_MTHD_SAME_CLASS)
    def determineOnlyMO(self):
        self.op_list.add(SemanticOP.ONLY_MO)
    def determineMoModification(self):
        self.op_list.add(SemanticOP.MODIFY_MO)
    def determineNonM2M(self):
        self.op_list.add(SemanticOP.NON_M2M)
    def determineAddDeleteMthd(self):
        self.op_list.add(SemanticOP.ADD_DELETE_MTHD_SAME_CLASS)
    def determineModifyNoMthd(self):
        self.op_list.add(SemanticOP.MODIFY_NO_METHOD)
    def determineModifyConnect(self):
        self.op_list.add(SemanticOP.MODIFY_CONNECT)
    def determineModifyDisconnect(self):
        self.op_list.add(SemanticOP.MODIFY_DISCONNECT)

    def extractSemanticOperations(self, relations):
        is_modified=False
        method_involved = False
        if(relations.getConnectMOSize()>0 and relations.getDisConnectMOSize()==0):
            self.determineOnlyAdd()
        if (relations.getConnectMOSize() == 0 and relations.getDisConnectMOSize() > 0):
            self.determineOnlyDelete()

        if(relations.total_added_cls >0  and relations.total_deleted_cls==0):
            self.determineOnlyAdd()
        if(relations.total_added_cls ==0  and relations.total_deleted_cls>0):
            self.determineOnlyDelete()
        if(relations.total_modified_cls>0):
            is_modified = True
            # self.determineOnlyModify()
        if(relations.contain_only_add_mthd>0 ):
            method_involved = True
            self.determineNewMethod()
        if (relations.contain_only_add_mthd_with_api > 0):
            self.determineNewApiMethod()
            method_involved = True
        if(relations.contain_only_delete_mthd>0):
            method_involved = True
            self.determineDeleteMethod()
        if(relations.contain_only_delete_mthd_with_api>0):
            self.determineDeleteApiMethod()
            method_involved = True

        if(relations.contain_add_delete_mthd>0):
            method_involved = True
            self.determineAddDeleteMthd()
        if (relations.contain_add_delete_mthd_with_api > 0):
            method_involved = True
            self.determineAddDeleteApiMthd()
        if(relations.total_non_m2m>0):
            self.determineNonM2M()
        if(is_modified and method_involved==False):
            # self.determineModifyNoMthd()
            if(relations.modify_connect):
                self.determineModifyConnect()
            if(relations.modify_disconnect):
                self.determineModifyDisconnect()

class RuleName(OperationRule):
    @staticmethod
    def getOpNameList():
        return [SemanticOP.NEW_MO.name ,
                SemanticOP.DELETE_MO.name,
                SemanticOP.CLASS_ADD.name,
                SemanticOP.CLASS_DELETE.name,
                SemanticOP.CLASS_MOVE.name,
                SemanticOP.MODIFY_NEW_METHOD.name,
                SemanticOP.MODIFY_DELETE_METHOD.name  ,
                SemanticOP.MODIFY_NEW_API_METHOD.name,
                SemanticOP.MODIFY_DELETE_API_METHOD.name,
                SemanticOP.METHOD_MOVE.name,
                SemanticOP.CONSTRUCTOR_MODIFY.name,
                SemanticOP.MODIFY_CONNECT.name ,
                SemanticOP.MODIFY_DISCONNECT.name ,
                SemanticOP.MODIFY_API_CONNECT.name,
                SemanticOP.MODIFY_API_DISCONNECT.name ,
                SemanticOP.MO_CONNECT.name ,
                SemanticOP.MO_DISCONNECT.name]
    def __init__(self):
        super().__init__()
    def determineClsAdd(self):
        self.op_list.add(SemanticOP.CLASS_ADD.name)
    def determineClsDelete(self):
        self.op_list.add(SemanticOP.CLASS_DELETE.name)
    def determineNewJpms(self):
        self.op_list.add(SemanticOP.NEW_MO.name)
    def determineDeleteJpms(self):
        self.op_list.add(SemanticOP.DELETE_MO.name)
    def determineMOConnect(self):
        self.op_list.add(SemanticOP.MO_CONNECT.name)
    def determineMODisconnect(self):
        self.op_list.add(SemanticOP.MO_DISCONNECT.name)
    def determineOnlyAdd(self):
        self.op_list.add(SemanticOP.ONLY_ADD.name)
    def determineOnlyDelete(self):
        self.op_list.add(SemanticOP.ONLY_DELETE.name)
    def determineOnlyModify(self):
        self.op_list.add(SemanticOP.ONLY_MODIFY.name)
    def determineNewMethod(self):
        self.op_list.add(SemanticOP.MODIFY_NEW_METHOD.name)
    def determineDeleteMethod(self):
        self.op_list.add(SemanticOP.MODIFY_DELETE_METHOD.name)
    def determineNewApiMethod(self):
        self.op_list.add(SemanticOP.MODIFY_NEW_API_METHOD.name)
    def determineDeleteApiMethod(self):
        self.op_list.add(SemanticOP.MODIFY_DELETE_API_METHOD.name)
    def determineAddDeleteApiMthd(self):
        print(SemanticOP.ADD_DELETE_API_MTHD_SAME_CLASS.name)
        self.op_list.add(SemanticOP.ADD_DELETE_API_MTHD_SAME_CLASS.name)
    def determineOnlyMO(self):
        self.op_list.add(SemanticOP.ONLY_MO.name)
    def determineMoModification(self):
        self.op_list.add(SemanticOP.MODIFY_MO.name)
    def determineNonM2M(self):
        self.op_list.add(SemanticOP.NON_M2M.name)
    def determineAddDeleteMthd(self):
        print(SemanticOP.ADD_DELETE_MTHD_SAME_CLASS.name)
        self.op_list.add(SemanticOP.ADD_DELETE_MTHD_SAME_CLASS.name)
    def determineModifyNoMthd(self):
        self.op_list.add(SemanticOP.MODIFY_NO_METHOD.name)
    def determineModifyConnect(self):
        self.op_list.add(SemanticOP.MODIFY_CONNECT.name)
    def determineModifyDisconnect(self):
        self.op_list.add(SemanticOP.MODIFY_DISCONNECT.name)
    def determineModifyConnectAPI(self):
        print(SemanticOP.MODIFY_API_CONNECT.name)
        self.op_list.add(SemanticOP.MODIFY_API_CONNECT.name)
    def determineModifyDisconnectAPI(self):
        print(SemanticOP.MODIFY_API_DISCONNECT.name)
        self.op_list.add(SemanticOP.MODIFY_API_DISCONNECT.name)
    def determineClassMov(self):
        # print(SemanticOP.CLASS_MOVE.name)
        self.op_list.add(SemanticOP.CLASS_MOVE.name)
    def determineMethodMov(self):
        # print(SemanticOP.METHOD_MOVE.name)
        self.op_list.add(SemanticOP.METHOD_MOVE.name)

    def determineModifyConstructor(self):
        # print(SemanticOP.CONSTRUCTOR_MODIFY.name)
        self.op_list.add(SemanticOP.CONSTRUCTOR_MODIFY.name)

    def extractDetailsSCO(self, relations):
        is_modified=False
        method_involved = False
        if(relations.n_add_mo>0):
            self.determineNewJpms()
        if (relations.n_delete_mo > 0):
            self.determineDeleteJpms()
        if(relations.getConnectMOSize()>0):
            self.determineMOConnect()
        if (relations.getDisConnectMOSize() > 0):
            self.determineMODisconnect()

        if((relations.total_added_cls - relations.getClsMoveInAddsize())>0):
            self.determineClsAdd()
        if(relations.getMoveClassSize()>0):
            self.determineClassMov()
        if(relations.getMoveMethodSize()>0):
            self.determineMethodMov()
        if((relations.total_deleted_cls - relations.getClsMoveInDeletesize())>0):
            self.determineClsDelete()
        if(relations.total_modified_cls>0):
            is_modified = True
            # self.determineOnlyModify()
        if((relations.getAddedConstructorSize()+relations.getDeleteConstructorSize())>0):
            self.determineModifyConstructor()
        # if(relations.getMoveInAddMethodSize()>0):
        #     self.determineMethodMov()
        if(((relations.getTotalAddMethodSize()) - (relations.getAddedConstructorSize()+ relations.getMoveInAddMethodSize()))>0):
            if(relations.getNewMthdSize()>0 ):
                method_involved = True
                self.determineNewMethod()
            if (relations.getNewAPIMthdSize() > 0):
                self.determineNewApiMethod()
                method_involved = True
        if(((relations.getTotalDeleteMethodSize()) - (relations.getDeleteConstructorSize()+ relations.getMoveMethodinDelete()))>0):
            if(relations.getDeletMthdSize()>0):
                method_involved = True
                self.determineDeleteMethod()
            if(relations.getDeletAPIMthdSize()>0):
                self.determineDeleteApiMethod()
                method_involved = True

        if(relations.getAddDeletMthdSize()>0):
            method_involved = True
            self.determineAddDeleteMthd()
        if (relations.getAddDeletAPIMthdSize() > 0):
            method_involved = True
            self.determineAddDeleteApiMthd()
        if(relations.total_non_m2m>0):
            self.determineNonM2M()
        if(is_modified):
            # self.determineModifyNoMthd()
            if(relations.getConnectModSize()>0):
                self.determineModifyConnect()
            if(relations.getDisConnectModSize()>0):
                self.determineModifyDisconnect()
            if(relations.getConnectApiSize()>0):
                self.determineModifyConnectAPI()
            if(relations.getDisConnectApiSize()>0):
                self.determineModifyDisconnectAPI()
    def extractSemanticOperations(self, relations):
        super().extractSemanticOperations(relations)

