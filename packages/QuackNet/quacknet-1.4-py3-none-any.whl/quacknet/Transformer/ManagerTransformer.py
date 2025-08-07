from quacknet.core.optimisers import Adam
from quacknet.core.lossFunctions import MSELossFunction

class Transformer:
    def __init__(self):
        self.adam = Adam(self.forwardPropagation, self.backwardPropagation)
        
        self.blocks = {}

    def addBlock(self, block):
        self.blocks.update({len(self.blocks): block})
    
    def forwardPropagation(self, input):
        for key in self.blocks:
            if(key == 0):
                input = self.blocks[key].forwardPropagation(input)
            else:
                input = self.blocks[key].forwardPropagation(input, False)
        return input

    def backwardPropagation(self, output, labels):
        Parameters = {}
        Gradients = {}
        for blockKey in self.blocks:
            Param, Grad = self.blocks[blockKey].backwardPropagation(output, labels)

            for key in Param:
                Parameters.update({f"{blockKey}.{key}": Param[key]}) # block key: 2, key: ATT_WO
                Gradients.update({f"{blockKey}.{key}": Grad[key]})   # will become 2.ATT_WO
        
        return Parameters, Gradients

    def optimiser(self, inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon):
        AllOutputs, Parameters = self.adam.optimiser(inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon)       
        # Parameters will be like [b1.w1, b1.w2 ... b2.w1, b2.w2 ... bn.w1, b2.w2]
        for i in range(len(self.blocks)):
            self.blocks[i].norm1.gamma = Parameters[f"{i}.Norm1_gamma"]
            self.blocks[i].norm1.beta = Parameters[f"{i}.Norm1_beta"] 
            self.blocks[i].norm2.gamma = Parameters[f"{i}.Norm2_gamma"] 
            self.blocks[i].norm2.beta = Parameters[f"{i}.Norm2_beta"]
            self.blocks[i].FFN.W1 = Parameters[f"{i}.FFN_W1"] 
            self.blocks[i].FFN.b1 = Parameters[f"{i}.FFN_b1"] 
            self.blocks[i].FFN.W2 = Parameters[f"{i}.FFN_W2"] 
            self.blocks[i].FFN.b2 = Parameters[f"{i}.FFN_b2"] 
            self.blocks[i].attention.outputWeight = Parameters[f"{i}.ATT_WO"] 
            self.blocks[i].attention.outputBias = Parameters[f"{i}.ATT_BO"] 
            self.blocks[i].attention.QueryWeights = Parameters[f"{i}.ATT_WQ"] 
            self.blocks[i].attention.KeyWeights = Parameters[f"{i}.ATT_WK"] 
            self.blocks[i].attention.ValueWeights = Parameters[f"{i}.ATT_WV"]
            if(i == 0):
                self.blocks[i].embedding.weights = Parameters[f"{i}.Embed_W"]

        return AllOutputs, Parameters

    def train(self, inputData, labels, useBatches = False, batchSize = 16, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        AllOutputs, self.Parameters = self.optimiser(inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon)
        loss = MSELossFunction(AllOutputs, labels)
        return loss