#	Copyright 2015 Place Pixel, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from math import sqrt


class UnionFind:
    """
    UnionFind data structure based on array index references
    """
    def __init__(self, n):
        self.parent = [i for i in range(n)]
        self.size = [1 for i in range(n)]

    def find(self, v_index):
        while (v_index != self.parent[v_index]):
            v_index = self.parent[v_index]
        return v_index

    def union(self, v_index_1, v_index_2):
        i = self.find(v_index_1)
        j = self.find(v_index_2)
        if (i == j):
            return i
        if (self.size[i] < self.size[j]):
            self.parent[i] = j
            self.size[j] += self.size[i]
            return j
        else:
            self.parent[j] = i
            self.size[i] += self.size[j]
            return i


def _complete_graph(xy_list):
    """
    Construct complete graph from xy-coordinates (including distance between coordinate pairs)
    """
    n = len(xy_list)
    graph = []
    for i in range(n):
        for j in range(i+1, n):
            coord_1 = xy_list[i]
            coord_2 = xy_list[j]
            [x_1, y_1] = coord_1
            [x_2, y_2] = coord_2
            dist = sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2)
            graph.append([dist, coord_1, coord_2])
    return graph


def _cluster_filter(xy_list, graph, cutoff):
    """
    Obtain MST cluster with at cutoff (percentage) of the coordinates
    """
    if not 0 <= cutoff <= 1:
        print("CUTOFF PERCENTAGE MUST BE BETWEEN 0 AND 1")
        exit(1)
    n = len(xy_list)
    coord_to_index = {str(xy_list[i]): i for i in range(n)}
    graph.sort(key=lambda entry: entry[0])
    clusters = UnionFind(n)
    for i in range(len(graph)):
        [dist, coord_1, coord_2] = graph[i]
        v_index_1 = coord_to_index[str(coord_1)]
        v_index_2 = coord_to_index[str(coord_2)]
        root = clusters.union(v_index_1, v_index_2)
        if (clusters.size[root] >= cutoff * n):
            break
    good_vertices = [xy_list[i] for i in range(n) if root == clusters.find(i)]
    return good_vertices


def _fit_box(good_vertices):
    """
    Fit box around extreme x and y values of coordinate list
    """
    n = len(good_vertices)
    good_vertices.sort(key=lambda coord: coord[0])
    x_min = good_vertices[0][0]
    x_max = good_vertices[n-1][0]
    good_vertices.sort(key=lambda coord: coord[1])
    y_min = good_vertices[0][1]
    y_max = good_vertices[n-1][1]
    return [[x_min, y_min], [x_max, y_max]]


def _scale_dimensions(bound_box, factor):
    """
    Scale dimensions of bounded box by a certain factor
    """
    if (factor <= 0):
        raise Exception("scaling factor must be positive")
        exit(1)
    [[x_min, y_min], [x_max, y_max]] = bound_box
    x_avg_diff = (x_max-x_min) / 2.0
    y_avg_diff = (y_max-y_min) / 2.0
    x_scale = (factor - 1) * x_avg_diff
    y_scale = (factor - 1) * y_avg_diff
    return [[(x_min - x_scale), (y_min - y_scale)], [(x_max + x_scale), (y_max + y_scale)]]


def _is_in_box(coord, bound_box):
    """
    Check whether a coordinate is inside a bounded box
    """
    [x, y] = coord
    [[x_min, y_min], [x_max, y_max]] = bound_box
    return (x_min <= x <= x_max) and (y_min <= y <= y_max)


def bound_box_coords(xy_list, cutoff):
    """
    Find [[x_min, y_min], [x_max, y_max]] from a set of xy-coordinates
    Cutoff parameter allows you to choose what percentage of points you want (0.9, 0.8, etc.)
    """
    graph = _complete_graph(xy_list)
    good_vertices = _cluster_filter(xy_list, graph, cutoff)
    bound_box = _fit_box(good_vertices)
    bound_box = _scale_dimensions(bound_box, 2)
    good_vertices = [coord for coord in xy_list if _is_in_box(coord, bound_box)]
    bound_box = _fit_box(good_vertices)
    return bound_box
