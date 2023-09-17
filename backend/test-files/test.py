# libraries
import os
from scipy.interpolate import interp1d
import cv2, vptree, PIL
import deeplake
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import directed_hausdorff
from skimage.feature import hessian_matrix, hessian_matrix_eigvals
from flask import Flask, send_file, request, jsonify, json


ds = deeplake.load('hub://activeloop/wiki-art')
dataloader = ds.pytorch(num_workers=0, batch_size=4, shuffle=False)



app = Flask(__name__)

@deeplake.compute
def filter_labels(sample_in, labels_list):
    return sample_in.labels.data()['text'][0] not in labels_list


@app.route("/process_drawing_array", methods=['POST'])
def process_drawing_array():

    folder_name = 'data'
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, folder_name)

    # Get a list of all .npy files in the folder
    npy_files = [f for f in os.listdir(folder_path) if f.endswith('.npy')]

    data = request.json  # Assuming data is sent as JSON
    arr = data.get('arr', [])  # Access the 'arr' field in the JSON data

    arr = [(subarr['x'], subarr['y']) for subarr in arr]
    arr = np.array(arr)

    #print(arr)
    #print(type(arr))

    # Load array 0
    arr = arr.reshape(-1, 2)
    array_0 = arr
    print(arr)


    min_distance = None
    min_file = None
    break_loop = False

    # Calculate the Hausdorff distance for each array (1-21) with array 0
    for root, dirs, files in os.walk(folder_path):
        if (break_loop):
            break
        for file in files:
            if file.endswith('.npy') and not file.endswith('.dat.npy'):
                # Construct the full file path
                filename = os.path.join(root, file)

                # Load the NumPy array from the file
                array_i = np.load(filename)
                
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

                ## Calculate the directed Hausdorff distance
                distance_0_to_i = directed_hausdorff(array_0_normalized, array_i_normalized)[0]

                if min_file is None:
                    min_distance = distance_0_to_i
                    min_file = filename
                else:
                    if (distance_0_to_i < min_distance):
                        min_distance = distance_0_to_i
                        min_file = filename

                print(filename, "= ", distance_0_to_i ," vs ", min_distance, min_file)
                if (min_distance < 300): 
                    break_loop = True
                    break

    print(min_distance)
    print(min_file)


    closest_array = np.load(os.path.join(folder_path, min_file))

    # Create a scatter plot for arr0 in blue and the closest array in red
    plt.scatter(array_0[:, 0], array_0[:, 1], label='arr0', color='blue', marker='o')
    plt.scatter(closest_array[:, 0], closest_array[:, 1], label=f'Closest (Distance: {min_distance:.2f})', color='red', marker='x')

    # Add labels and a legend
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.title('Scatter Plot of arr0 and Closest Array')
    plt.show()

    index = int(os.path.basename(os.path.dirname(min_file)))
    img = image = ds.images[index].numpy()

    ret, image_encoded = cv2.imencode(".jpg", img)
    if ret:
        # Decode the image from the encoded format
        decoded_image = cv2.imdecode(image_encoded, 1)  # Use '1' for color images, '0' for grayscale
    
        #cv2.imshow("Decoded Image", decoded_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
    else:
        print("Error encoding the image.")
    np.set_printoptions(threshold=np.inf)
    #return decoded_image

    return "aa"

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
