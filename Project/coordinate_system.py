import cv2
import os
import numpy as np

def get_coordinateSystem():
    
    matrix=0

    # Function to capture an image from the camera
    def capture_image():
        cap = cv2.VideoCapture(0)  # Open the default camera
        if not cap.isOpened():
            raise Exception("Could not open video device")

        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise Exception("Failed to capture image")

        return frame

    # Function to calculate the transformation matrix
    def calculate_transformation_matrix(p1, p2, p3):
        pts_src = np.array([p1, p2, p3], dtype=np.float32)
        pts_dst = np.array([[0, 0], [0, 10], [10, 0]], dtype=np.float32)

        matrix = cv2.getAffineTransform(pts_src, pts_dst)
        return matrix

    # Function to apply the transformation to a point
    def apply_transformation(matrix, point):
        print(matrix)
        pts = np.array([point], dtype=np.float32).reshape(-1, 1, 2)
        transformed_pts = cv2.transform(pts, matrix)
        return transformed_pts[0][0]

    # Mouse callback function to select points
    def select_points(event, x, y, flags, param):
        global points, image, display_image
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            if len(points) == 4:
                cv2.destroyAllWindows()
        elif event == cv2.EVENT_MOUSEMOVE:
            display_image = image.copy()
            cv2.line(display_image, (x - 10, y), (x + 10, y), (0, 255, 0), 1)
            cv2.line(display_image, (x, y - 10), (x, y + 10), (0, 255, 0), 1)

    # Function to save configuration to a file
    def save_to_file(points, matrix, transformed_point, filename="Project/txt/config.txt"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as file:
            for idx, point in enumerate(points[:3], start=1):
                file.write(f'P{idx}: {point[0]},{point[1]}\n')
            file.write(f'P4: {points[3][0]},{points[3][1]}\n')
            file.write('\nTransformation Matrix:\n')
            for row in matrix:
                file.write(' '.join(map(str, row)) + '\n')
            file.write(f'\nTransformed P4: {transformed_point[0]},{transformed_point[1]}\n')

    # Main function
    def main():
        global points, image, display_image
        points = []

        # Capture an image
        image = capture_image()

        # Set up display image
        display_image = image.copy()

        # Display the image and set the mouse callback
        cv2.imshow("Select 4 Points", display_image)
        cv2.setMouseCallback("Select 4 Points", select_points)

        point_names = ["P1 (0,0)", "P2 (0,10)", "P3 (10,0)", "P4"]

        while len(points) < 4:
            if len(points) < 4:
                cv2.putText(display_image, f"Select {point_names[len(points)]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Select 4 Points", display_image)
            cv2.waitKey(1)

        cv2.destroyAllWindows()

        # Calculate the transformation matrix
        matrix = calculate_transformation_matrix(points[0], points[1], points[2])

        # Transform the fourth point
        transformed_p4 = apply_transformation(matrix, points[3])

        # Save the points and transformation matrix to a file
        save_to_file(points, matrix, transformed_p4)

        print(f"Transformation matrix and points saved to txt/config.txt:\n{matrix}")
        print(f"Transformed P4: {transformed_p4}")
        return matrix

  
    main()
        
    return matrix
        