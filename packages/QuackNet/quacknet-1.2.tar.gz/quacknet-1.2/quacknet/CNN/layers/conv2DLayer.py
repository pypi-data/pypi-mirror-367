import numpy as np
import math

class Conv2DLayer():
    def __init__(self, kernalSize, depth, numKernals, stride, padding = "no"):
        """
        Initialises a convolutional layer.

        Args:
            kernalSize (int): The size of the covolution kernel (assumed it is a square).
            depth (int): Depth of the input tensor.
            numKernals (int): Number of kernels in this layer.
            stride (int): The stride length for convolution.
            padding (str or int, optional): Padding size or "no" for no padding. Default is "no".
        """
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
        """
        Pads each image in the input tensor.

        Args:
            inputTensor (ndarray): A 3D array representing the images with shape (number of images, height, width).
            kernalSize (int): The size of the covolution kernel (assumed it is a square).
            strideLength (int): The stride length for convolution.
            typeOfPadding (int): The value used for padding the images.
        
        Returns:
            ndarray: A 3D array of padded images.
        """
        paddingTensor = []
        for image in inputTensor:
            paddingSize = math.ceil(((strideLength - 1) * len(image) - strideLength + kernalSize) / 2)
            padding = np.full((image.shape[0] + paddingSize * 2, image.shape[1] + paddingSize * 2), typeOfPadding) #creates an 2d numpy array of size paddingSize x paddingSize
            padding[paddingSize: paddingSize + image.shape[0], paddingSize: paddingSize + image.shape[1]] = image
            paddingTensor.append(padding)
        return np.array(paddingTensor)

    def forward(self, inputTensor):
        """
        Performs the convolution operation on the input tensor.

        Args:
            inputTensor (ndarray): A 3D array representing the images with shape (number of images, height, width).

        Returns:
             ndarray: Output tensor after convolution.
        """
        tensorKernals = []
        if(self.usePadding == True):
            imageTensor = self._padImage(inputTensor, self.kernalSize, self.stride, self.padding)
        else:
            imageTensor = inputTensor
        outputHeight = (imageTensor.shape[1] - self.kernalSize) // self.stride + 1
        outputWidth = (imageTensor.shape[2] - self.kernalSize) // self.stride + 1
        for i in range(len(self.kernalWeights)):
            output = np.zeros((outputHeight, outputWidth))
            kernal = self.kernalWeights[i]
            biases = self.kernalBiases[i]
            for x in range(outputHeight):
                indexX = x * self.stride
                for y in range(outputWidth):
                    indexY = y * self.stride
                    gridOfValues = imageTensor[:, indexX: indexX + self.kernalSize, indexY: indexY + self.kernalSize] # 2d grid
                    dotProduct = np.sum(gridOfValues * kernal) 
                    output[x, y] = dotProduct + biases
                    
            tensorKernals.append(output)
        return np.stack(tensorKernals, axis = 0) #tensorKernals = (outputHeight, outputWidth, numberOfKernals)
                    
    def _backpropagation(self, errorPatch, inputTensor):
        """
        Compute gradients for conolutional layer weights, biases and input errors during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the convolutional layer during forward propagation.
        
        Returns:
            weightGradients (ndarray): Gradients of the loss with respect to kernels.
            biasGradients (ndarray): Gradients of the loss with respect to biases for each kernel.
            inputErrorTerms (ndarray): Error terms propagated to the previous layer.
        """
        ###################################        
        # gets the error gradient from the layer infront and it is a error patch
        # this error patch is the same size as what the convolutional layer outputed during forward propgation
        # get the kernal (as in a patch of the image) again, but this time you are multipling each value in the kernal by 1 value that is inside the error patch
        # this makes the gradient of the loss of one kernal's weight
        
        # the gradient of the loss of one kernal's bias is the summ of all the error terms
        # because bias is applied to every input in forward propgation
        
        # the gradient of the loss of the input, which is the error terms for the layer behind it
        # firstly the kernal has to be flipped, meaning flip the kernal left to right and then top to bottom, but not flipping the layers,
        # the gradient of one pixel, is the summ of each error term multiplied by the flipped kernal 
        ###################################     
        
        kernalSize = self.kernalSize # all kernals are the same shape and squares
        weightGradients = np.zeros((len(inputTensor), len(self.kernalWeights), kernalSize, kernalSize)) #kernals are the same size
        outputHeight, outputWidth = errorPatch.shape[1], errorPatch.shape[2]
        for output in range(len(self.kernalWeights)):
            for layer in range(len(inputTensor)):
                for i in range(outputHeight):
                    for j in range(outputWidth):
                        startI = i * self.stride
                        startJ = j * self.stride
                        if(startI + kernalSize > inputTensor.shape[1] or startJ + kernalSize > inputTensor.shape[2]):
                            continue
                        kernal = inputTensor[layer, startI: startI + kernalSize, startJ : startJ + kernalSize]
                        weightGradients[layer, output] += kernal * errorPatch[output, i, j]
    
        biasGradients = np.sum(errorPatch, axis=(1, 2))

        inputErrorTerms = np.zeros_like(inputTensor)
        flipped = self.kernalWeights[:, :, ::-1, ::-1]
        for output in range(len(errorPatch)):
            for layer in range(len(inputTensor)):
                for i in range(outputHeight):
                    inputI = i * self.stride
                    for j in range(outputWidth):
                        inputJ = j * self.stride
                        if(inputI + kernalSize > inputTensor.shape[1] or inputJ + kernalSize > inputTensor.shape[2]):
                            continue
                        errorKernal = errorPatch[output, i, j]
                        inputErrorTerms[layer, inputI: inputI + kernalSize, inputJ: inputJ + kernalSize] += errorKernal * flipped[output, layer]
        
        weightGradients = np.transpose(weightGradients, (1, 0, 2, 3))
        return weightGradients, biasGradients, inputErrorTerms
    
    