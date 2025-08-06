import numpy as np

class GlobalAveragePooling():
    def forward(self, inputTensor):
        """
        Performs global average pooling, reducing each feuture map to a single value.

        Args:
            inputTensor (ndarray): A 3D array representing the images with shape (number of images, height, width).
        
        Returns:
            ndarray: A 2D array containing global averages for each feuture map.
        """
        output = np.mean(inputTensor, axis = (1, 2))
        return output

    def _backpropagation(self, inputTensor):
        """
        Compute the gradient of the loss with respect to the input of the global average pooling layer during backpropagation.

        Args:
            inputTensor (ndarray): Input to the global average pooling layer during forward propagation.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """     
        return np.ones_like(inputTensor) * (1 / (inputTensor.shape[1] * inputTensor.shape[2]))