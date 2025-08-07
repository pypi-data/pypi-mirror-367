import numpy as np

class GlobalAveragePooling():
    def forward(self, inputTensor):
        """
        Performs global average pooling, reducing each feuture map to a single value.

        Args:
            inputTensor (ndarray): A 4D array representing the images with shape (batches, number of images, height, width).
        
        Returns:
            ndarray: A 3D array containing global averages for each feuture map for each batch.
        """
        self.inputShape = inputTensor.shape
        output = np.mean(inputTensor, axis = (2, 3))
        return output

    def _backpropagation(self, gradient):   
        batch_size, channels, height, width = self.inputShape

        grad = np.zeros((batch_size, channels, height, width), dtype=np.float64)

        for b in range(batch_size):
            for c in range(channels):
                grad[b, c] = gradient[b, c] / (height * width)
        
        return grad