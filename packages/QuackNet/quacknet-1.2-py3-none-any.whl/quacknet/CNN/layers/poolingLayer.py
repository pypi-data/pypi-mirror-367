import numpy as np

class PoolingLayer():
    def __init__(self, gridSize, stride, mode = "max"):
        """
        Initialises a pooling layer.

        Args:
            gridSize (int): The size of the pooling window.
            stride (int): The stride length for pooling.
            mode (str, optional): Pooling mode of "max", "ave" (average). Default is "max".        
        """
        self.gridSize = gridSize
        self.stride = stride
        self.mode = mode.lower()
    
    def forward(self, inputTensor):
        """
        Applies pooling (max or average) to reduce the size of the batch of inputs.

        Args:
            inputTensor (ndarray): A 3D array representing the images with shape (number of images, height, width).

        Returns:
            ndarray: A 3D array of feuture maps with reduced shape.
        """
        tensorPools = []

        if(self.mode.lower() == "max"):
            poolFunc = np.max
        elif(self.mode.lower() == "ave"):
            poolFunc = np.mean
        else:
            raise ValueError(f"pooling mode isnt correct: '{self.mode}', expected 'max' or 'ave'")

        for image in inputTensor: # tensor is a 3d structures, so it is turning it into a 2d array (eg. an layer or image)
            outputHeight = (image.shape[0] - self.gridSize) // self.stride + 1
            outputWidth = (image.shape[1] - self.gridSize) // self.stride + 1
            output = np.zeros((outputHeight, outputWidth))
            for x in range(outputHeight):
                for y in range(outputWidth):
                    indexX = x * self.stride
                    indexY = y * self.stride
                    gridOfValues = image[indexX: indexX + self.gridSize, indexY: indexY + self.gridSize]
                    output[x, y] = poolFunc(gridOfValues)
            tensorPools.append(output)
        return np.array(tensorPools)

    def _backpropagation(self, errorPatch, inputTensor):
        """
        Performs backpropagation through the pooling layer.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input tensor during forward propagation.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss.
        """
        if(self.mode == "max"):
            return self._MaxPoolingDerivative(errorPatch, inputTensor, self.gridSize, self.stride)
        elif(self.mode == "ave"):
            return self._AveragePoolingDerivative(errorPatch, inputTensor, self.gridSize, self.stride)

    def _MaxPoolingDerivative(self, errorPatch, inputTensor, sizeOfGrid, strideLength):
        """
        Compute the gradient of the loss with respect to the input of the max pooling layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the max pooling layer during forward propagation.
            sizeOfGrid (int): Size of the pooling window.
            strideLength (int): Stride length used during pooling.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """
        inputGradient = np.zeros_like(inputTensor, dtype=np.float64)
        outputHeight = (inputTensor.shape[1] - sizeOfGrid) // strideLength + 1
        outputWidth = (inputTensor.shape[2] - sizeOfGrid) // strideLength + 1
        for image in range(len(inputTensor)): # tensor is a 3d structures, so it is turning it into a 2d array (eg. an layer or image)
            for x in range(outputHeight):
                for y in range(outputWidth):
                    indexX = x * strideLength
                    indexY = y * strideLength

                    gridOfValues = inputTensor[image, indexX: indexX + sizeOfGrid, indexY: indexY + sizeOfGrid]
                    indexMax = np.argmax(gridOfValues)
                    maxX, maxY = divmod(indexMax, sizeOfGrid)

                    #newValues = np.zeros((sizeOfGrid, sizeOfGrid))
                    #newValues[maxX, maxY] = 1
                    #inputGradient[image, indexX: indexX + sizeOfGrid, indexY: indexY + sizeOfGrid] += newValues * errorPatch[image, x, y]

                    inputGradient[image, indexX + maxX, indexY + maxY] += errorPatch[image, x, y]
        return inputGradient

    def _AveragePoolingDerivative(self, errorPatch, inputTensor, sizeOfGrid, strideLength):
        """
        Compute the gradient of the loss with respect to the input of the average pooling layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the average pooling layer during forward propagation.
            sizeOfGrid (int): Size of the pooling window.
            strideLength (int): Stride length used during pooling.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """       
        inputGradient = np.zeros_like(inputTensor, dtype=np.float32)
        outputHeight = (inputTensor.shape[1] - sizeOfGrid) // strideLength + 1
        outputWidth = (inputTensor.shape[2] - sizeOfGrid) // strideLength + 1
        avgMultiplier = 1 / (sizeOfGrid ** 2)
        for image in range(len(inputTensor)): # tensor is a 3d structures, so it is turning it into a 2d array (eg. an layer or image)
            for x in range(outputHeight):
                for y in range(outputWidth):
                    indexX = x * strideLength
                    indexY = y * strideLength
                    #newValues = np.ones((sizeOfGrid, sizeOfGrid)) * errorPatch[image, x, y] / (sizeOfGrid ** 2)
                    newValues = errorPatch[image, x, y] * avgMultiplier
                    inputGradient[image, indexX: indexX + sizeOfGrid, indexY: indexY + sizeOfGrid] += newValues 
        return inputGradient