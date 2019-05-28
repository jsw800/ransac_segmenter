#!/usr/bin/python3
import math
import numpy

# from PyQt5.QtCore import QPointF
x = 0
y = 1


def sortByX(array):
    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = array[0][x]

        for element in array:
            if element[x] - 30 < pivot < element[x] + 30:
                equal.append(element)
            elif element[x] < pivot:
                less.append(element)
            elif element[x] > pivot:
                greater.append(element)
        return sortByX(less) + equal + sortByX(greater)  # Just use the + operator to join lists
    else:
        return array


def find_angle(array):
    right_vertex = array[0]
    i = len(array) - 1
    j = len(array) - 1
    while i > 0:
        pointA = array[i]
        distA = ((((pointA[x] - right_vertex[x]) ** 2) + ((pointA[y] - right_vertex[y]) ** 2)) ** .5)
        if 50 > math.fabs(pointA[x] - right_vertex[x]):
            while j > 1:
                pointB = array[j]
                distB = ((((pointB[x]-right_vertex[x])**2)+((pointB[y]-right_vertex[y])**2))**.5)
                if 50 > math.fabs(pointB[y] - right_vertex[y]):
                    distC = ((((pointB[x]-pointA[x])**2)+((pointB[y]-pointA[y])**2))**.5)
                    test_angle = math.acos(((distA**2)+(distB**2)-(distC**2))/(2*distA*distB))
                    if (math.pi/2) - .02 < test_angle < (math.pi/2) + .02:
                        pointC = [right_vertex[x] + 150, right_vertex[y]]
                        distD = ((((pointC[x]-right_vertex[x])**2)+((pointC[y]-right_vertex[y])**2))**.5)
                        distE = ((((pointA[x]-pointC[x])**2)+((pointA[y]-pointC[y])**2))**.5)
                        temp = ((distA**2)+(distD**2)-(distE**2))/(2*distA*distD)
                        if 1.1 > temp > 1:
                            temp = 1
                        elif -1.1 < temp < -1:
                            temp = -1
                        angle = (math.pi/2) - math.acos(temp)
                        return angle
                j = j - 1
        i = i - 1
    return 0


def transform_points(corners, rotation_matrix, pivot):
    i = 0
    while i < len(corners):
        temp_point = [[corners[i][x]-pivot[x]], [corners[i][y]-pivot[y]], [1]]
        new_point = numpy.matmul(rotation_matrix, temp_point)
        corners[i] = [new_point[0][0]+pivot[x], new_point[1][0]+pivot[y]]
        i = i+1
    return corners


def deskew_points(corners, angle):
    ccw_rotation_matrix = [[math.cos(angle), math.sin(-angle), 0],
                           [math.sin(angle), math.cos(angle), 0],
                           [0, 0, 1]]
    cw_rotation_matrix = [[math.cos(angle), math.sin(angle), 0],
                          [math.sin(-angle), math.cos(angle), 0],
                          [0, 0, 1]]
    pivot = corners[0]
    if angle < 0:
        corners = transform_points(corners, ccw_rotation_matrix, pivot)
    elif angle > 0:
        corners = transform_points(corners, cw_rotation_matrix, pivot)
    return corners


def reskew_points(columns, angle):
    ccw_rotation_matrix = [[math.cos(angle), math.sin(-angle), 0],
                           [math.sin(angle), math.cos(angle), 0],
                           [0, 0, 1]]
    cw_rotation_matrix = [[math.cos(angle), math.sin(angle), 0],
                          [math.sin(-angle), math.cos(angle), 0],
                          [0, 0, 1]]
    pivot = columns[0][0]
    if angle > 0:
        for i in range(len(columns)):
            columns[i] = transform_points(columns[i], ccw_rotation_matrix, pivot)
    elif angle < 0:
        for i in range(len(columns)):
            columns[i] = transform_points(columns[i], cw_rotation_matrix, pivot)
    return columns


def find_column_lines(deskewed_corners):
    array1 = []
    i = 0
    while i < len(deskewed_corners)-1:
        pivot = deskewed_corners[i]
        array2 = [pivot]
        for point in deskewed_corners[i+1:]:
            i = i + 1
            if -50 < point[x] - pivot[x] < 50:
                array2.append([point[x], point[y]])
            else:
                break
        array1.append(array2)
    return array1


def create_ranges(columns):
    ranges = []
    i = 0
    while i < len(columns)-2:
        j = 0
        while j < len(columns[i])-2 and j < len(columns[i+1])-2:
            cell_range = [round(min(columns[i][j][x], columns[i][j+1][x])),
                          round(max(columns[i+1][j][x], columns[i+1][j+1][x])),
                          round(min(columns[i][j][y], columns[i+1][j][y])),
                          round(max(columns[i][j+1][y], columns[i+1][j+1][y]))]
            ranges.append(cell_range)
            j = j + 1
        i = i + 1
    return ranges


def flatten_matrix(matrix):
    ptlist = []
    for i in range(matrix.shape[1]):
        ptlist.append([(int(matrix[x][i])), (int(matrix[y][i]))])
    return ptlist


def convert_points_into_ranges(unsorted_points):
    unsorted_points = flatten_matrix(unsorted_points)
    half_sorted_points = sorted(unsorted_points, key=lambda a: a[y])
    sorted_points = sortByX(half_sorted_points)

    angle = find_angle(sorted_points)
    if -0.05235988 > angle or angle > 0.05235988:
        sorted_points = deskew_points(sorted_points, angle)
    columns = find_column_lines(sorted_points)
    if -0.05235988 > angle or angle > 0.05235988:
        columns = reskew_points(columns, angle)
    ranges = create_ranges(columns)

    return ranges


class RangeCalculator:
    def __init__(self, display):
        self.points = None
        self.gui_display = display
