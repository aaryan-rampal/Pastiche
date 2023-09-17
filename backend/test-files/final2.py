# libraries
import os
import cv2, numpy, vptree, PIL
import matplotlib.pyplot as plt
from skimage.feature import hessian_matrix, hessian_matrix_eigvals

# main
#img = cv2.imread("rectangle.jpg", cv2.IMREAD_COLOR)
img2 = cv2.imread("circle.jpg", cv2.IMREAD_COLOR)
#img3 = cv2.imread("circle.jpg", cv2.IMREAD_COLOR)

#assert img is not None, "file could not be read, check with os.path.exists()"
#assert img2 is not None, "file could not be read, check with os.path.exists()"
#assert img3 is not None, "file could not be read, check with os.path.exists()"

numpy.set_printoptions(threshold=numpy.inf)

def grey_conversion(image):
    grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return grey_img

def blurring(image):
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    return blur
    
def canny_edge(image):
    edges = cv2.Canny(image, 50, 200)
    return edges

def ridge_detection(image):
    ridge_filter = cv2.ximgproc.RidgeDetectionFilter_create()
    ridges = ridge_filter.getRidgeFilteredImage(image)

def detect_ridges(grey, sigma=1.0):
    H_elems = hessian_matrix(grey, sigma=sigma, order='rc')
    maxima_ridges, minima_ridges = hessian_matrix_eigvals(H_elems)
    return maxima_ridges, minima_ridges

def plot_images(*images):
    images = list(images)
    n = len(images)
    fig, ax = plt.subplots(ncols=n, sharey=True)
    for i, img in enumerate(images):
        ax[i].imshow(img, cmap='gray')
        ax[i].axis('off')
    plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97)
    plt.show()
    
def euclidean(p1, p2):
  return numpy.sqrt(numpy.sum(numpy.power(p2 - p1, 2)))

def find_edge(image):
    grey = grey_conversion(image)

    blur = blurring(grey)
    
    edge = canny_edge(blur)
    
    edge_list = edge.tolist()
    """
    for edges in edge_list:
        print(edges)
        print("\n\n")
    """
    print(type(edge))
    
    contours, hierarchy = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    contour_list = []
    
    for contour in contours:
        if cv2.contourArea(contour) > 15:  # Adjust the area threshold as needed
            contour_list.append(contour)

    
        
        
    
    cntsSorted = sorted(contour_list, key=lambda x: cv2.contourArea(x))
    
    print("Number of Contours found = " + str(len(contour_list)))
    
    points = edge
    
    individual_edges_image = numpy.zeros_like(image)

    cv2.drawContours(individual_edges_image, cntsSorted, -1, (0, 255, 0), thickness=2)  # You can customize the color and thickness

    cv2.imwrite('individual_edges.jpg', individual_edges_image)
    
    tree = vptree.VPTree(points, euclidean)

    ridge_maxima, ridge_minima = detect_ridges(grey, sigma=3.0)

    return contour_list



contours = find_edge(img2)


if not os.path.exists("a"):
    os.makedirs("a")


output_dir = 'images'
os.makedirs(output_dir, exist_ok=True)

for i, contour in enumerate(contours):
    contour_image = numpy.zeros_like(img2)

    # Draw the current contour on the blank image
    cv2.drawContours(contour_image, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)

    # Save the contour image to a separate file
    contour_filename = os.path.join(output_dir, f'contour_{i}.jpg')
    cv2.imwrite(contour_filename, contour_image)

# Save each sub-list as a separate numpy file inside the "f" folder
for i, sublist in enumerate(contours):
    # Convert the sublist to a numpy array
    arr = numpy.array(sublist)
    #print(arr)

    min_x = numpy.min(arr[:, :, 0])  # Minimum of the first digit (x-coordinate)
    min_y = numpy.min(arr[:, :, 1])  # Minimum of the second digit (y-coordinate)

    arr[:, :, 0] -= min_x
    arr[:, :, 1] -= min_y

    arr = arr.reshape(-1, 2)

    # Define the filename for the numpy file
    filename = os.path.join("a", "array_{i}.npy")
    
    # Save the numpy array to the file
    numpy.save(filename, arr)
