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
        self.inputShape = inputTensor.shape
        output = np.mean(inputTensor, axis = (2, 3))
        return output

    def _backpropagation(self, gradient):   
        batch_size, channels, height, width = self.inputShape
        grad = np.ones((batch_size, channels, height, width), dtype=np.float64) * (1 / (height * width))

        return grad * gradient[:, :, None, None]