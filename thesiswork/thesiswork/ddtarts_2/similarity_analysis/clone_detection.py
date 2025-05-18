
class CodeToToekn:
    @staticmethod
    def codeToken(method1):
        block = Block()
        for line in method1:
            toks = line.replace(";", "").replace(",", " ").replace(".", " ").replace(")", " ").replace("<",
                                                                                                       " ").replace(">",
                                                                                                                    " ").replace(
                "{", " ").replace("}", " ").replace("+", " ").replace("(", " ").replace("[", " ").replace("]",
                                                                                                          " ").replace(
                "[", " "). \
                replace("*", " ").replace("/", " ").replace("%", " ").replace("-", " ").replace("&", " ").replace("=",
                                                                                                                  " ")\
                .replace("!", " ").replace("|"," ")
            toks = toks.split(" ")
            for tok in toks:
                tok = tok.replace(" ", "")
                if (tok == " "):
                    continue
                if (tok == ""):
                    continue

                block.pushToeken(tok)
        return block
class Block:
    def __init__(self):
        self.tokenmap = {}
        self.totalfreq = 0
    def getTotalFreq(self):
        return self.totalfreq

    def pushToeken(self, tok):
        if tok not in self.tokenmap.keys():
            self.tokenmap[tok] = 1
        else:
            self.tokenmap[tok] += 1
        self.totalfreq +=1

    def getToekenFreq(self, tok):
        if (tok in self.tokenmap.keys()):
            return self.tokenmap[tok]
        else:
            return 0
class Clone:
    def __init__(self, threshold):
        self.threshold = 0.50
    def isClone(self, block1, block2):
        maxb = Block()
        minb = Block()
        if(block1.getTotalFreq() >block2.getTotalFreq()):
            maxb = block1
            minb = block2
        else:
            maxb = block2
            minb = block1
        thresld = self.threshold* maxb.getTotalFreq()
        sharedtoken = 0
        remainingToken = maxb.getTotalFreq()
        #// Heuristic: Small block does not contain enough tokens to be a clone
        if(minb.getTotalFreq() <thresld):
            return False

        tokenlist = list(maxb.tokenmap.keys())
        for tok in tokenlist:
            maxfreq = maxb.getToekenFreq(tok)
            # print(maxfreq)
            minfreq = minb.getToekenFreq(tok)
            if(minfreq!=0):
                sharedtoken += min(minfreq,maxfreq)
            remainingToken -= maxfreq
        # print(sharedtoken, thresld)
        if(sharedtoken >= thresld):
            return True
        if(sharedtoken + remainingToken <thresld):
            return  False
