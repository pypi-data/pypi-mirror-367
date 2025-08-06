import numpy as np
import math

class Conv1DLayer():
    def __init__(self, kernalSize, depth, numKernals, stride, padding = "no"):
        self.kernalSize = kernalSize
        self.numKernals = numKernals
        self.kernalWeights = []
        self.kernalBiases = []
        self.depth = depth
        self.stride = stride
        self.padding = padding

        if(padding.lower() == "no" or padding.lower() == "n"):
            self.usePadding = False
        else:
            self.padding = int(self.padding)
            self.usePadding = True
    
    def _padImage(self, inputTensor, kernalSize, strideLength, typeOfPadding): #pads image
        depth, length = inputTensor.shape
        paddingSize = math.ceil(((strideLength - 1) * length - strideLength + kernalSize) / 2)

        paddedTensor = []
        for i in range(depth):
            original = inputTensor[i]
            padding = [typeOfPadding] * paddingSize
            padded = np.array(padding + list(original) + padding)
            paddedTensor.append(padded)
        return np.array(paddedTensor)

    def forward(self, inputTensor):
        if(self.usePadding == True):
            inputTensor = self._padImage(inputTensor, self.kernalSize, self.stride, self.padding)

        depth, seqLength = inputTensor.shape
        outputLength = (seqLength - self.kernalSize) // self.stride + 1
        output = np.zeros((self.numKernals, outputLength))
        
        for k in range(self.numKernals):
            kernal = self.kernalWeights[k]
            bias = self.kernalBiases[k]
            for i in range(outputLength):
                start = i * self.stride
                end = start + self.kernalSize
                region = inputTensor[:, start: end]

                if(region.shape != kernal.shape):
                    continue

                output[k, i] = np.sum(region * kernal) + bias
        return output
                    
    def _backpropagation(self, errorPatch, inputTensor): 
        if(self.usePadding == True):
            inputTensor = self._padImage(inputTensor)
        
        _, seqLength = inputTensor.shape
        outputLength = errorPatch.shape[1]
        weightGradients = np.zeros_like(self.kernalWeights)
        inputErrorTerms = np.zeros_like(inputTensor)

        for k in range(self.numKernals):
            for d in range(self.depth):
                for i in range(outputLength):
                    start = i * self.stride
                    end = start + self.kernalSize
                    if(end > seqLength):
                        continue
                    region = inputTensor[d, start: end]
                    weightGradients[k, d] += errorPatch[k, i] * region
        
        biasGradients = np.sum(errorPatch, axis = 1)

        flippedKernels = self.kernalWeights[:, :, ::-1]
        for k in range(self.numKernals):
            for d in range(self.depth):
                for i in range(outputLength):
                    start = i * self.stride
                    end = start + self.kernalSize
                    if(end > seqLength):
                        continue
                    inputErrorTerms[d, start: end] += errorPatch[k, i] * flippedKernels[k, d]
            
        return weightGradients, biasGradients, inputErrorTerms