# libraries
import os
from scipy.interpolate import interp1d
from flask import Flask, send_file, request, jsonify, json
import cv2, vptree, PIL
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import directed_hausdorff
from skimage.feature import hessian_matrix, hessian_matrix_eigvals

# Folder path containing the .npy files
folder_path = 'f'

# Get a list of all .npy files in the folder, excluding array_0.npy
npy_files = [f for f in os.listdir(folder_path) if f.endswith('.npy')]

#initialize Flask app 
app = Flask(__name__)

@app.route("/process_drawing_array", methods=['POST', 'GET'])
def process_drawing_array():
    data = request.json
    arr = data.get('arr', [])
    arr = [(subarr['x'], subarr['y']) for subarr in arr]
    array_0 = np.array(arr)

    min_distance = -1
    min_file = -1

    # Calculate the Hausdorff distance for each array (1-21) with array 0
    i = 0
    for filename in npy_files:
        filename = f'array_{i}.npy'
        array_i = np.load(os.path.join(folder_path, filename))
    
        # Determine the number of points you want for the rescaled arrays
        num_points = max(len(array_0), len(array_i))
    
        # Interpolate array_0 to match the size of array_i
        x0 = np.arange(len(array_0))
        f0 = interp1d(x0, array_0, axis=0, kind='linear')
        array_0_normalized = f0(np.linspace(0, len(array_0) - 1, num_points))
    
        # Interpolate array_i to match the size of array_0
        xi = np.arange(len(array_i))
        fi = interp1d(xi, array_i, axis=0, kind='linear')
        array_i_normalized = fi(np.linspace(0, len(array_i) - 1, num_points))

        ## Interpolate array_i to match the size of array_0
        #num_points = len(array_0)
        #x = np.arange(len(array_i))
        #f = interp1d(x, array_i, axis=0, kind='linear')
        #array_i_normalized = f(np.linspace(0, len(array_i) - 1, num_points))
        #
        ## Calculate the directed Hausdorff distance
        distance_0_to_i = directed_hausdorff(array_0_normalized, array_i_normalized)[0]

        if (i != 0):
            if (distance_0_to_i < min_distance):
                min_distance = distance_0_to_i
                min_file = filename
        else:
            min_distance = distance_0_to_i
            min_file = filename

        print(filename, "= ", distance_0_to_i ," vs ", min_distance, min_file)
    
        i += 1

        filename = 'starry-night.jpg' #TODO: GET CORRECT FILENAME
        return send_file(filename, mimetype='image/jpg')


if __name__ == '__main__':
    app.run(debug=True, port=5000)