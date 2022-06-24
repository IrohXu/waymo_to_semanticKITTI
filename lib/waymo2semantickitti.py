import os
import matplotlib.pyplot as plt
import tensorflow.compat.v1 as tf
import numpy as np

tf.enable_eager_execution()

from waymo_open_dataset.utils import  frame_utils
from waymo_open_dataset import dataset_pb2 as open_dataset
from waymo_open_dataset.protos import segmentation_metrics_pb2
from waymo_open_dataset.protos import segmentation_submission_pb2
from waymo_open_dataset.utils import range_image_utils, transform_utils
from waymo_open_dataset.utils.frame_utils import parse_range_image_and_camera_projection
from lib.utils import convert_range_image_to_point_cloud_labels

class Waymo2SemanticKITTI(object):
    """Waymo to SemanticKITTI converter.
    This class serves as the converter to change the waymo raw data to SemanticKITTI format.
    Args:

    """

    def __init__(self, load_dir, save_dir):
        self.load_dir = load_dir  # e.g. ~/waymo_open_dataset
        self.save_dir = save_dir  # e.g. ~/SemanticKITTI/dataset/sequences
        # self.save_velodyne = os.path.join(save_dir, "velodyne")
        # self.save_labels = os.path.join(save_dir, "labels")


    def create_lidar(self, frame):
        """Parse and save the lidar data in psd format.
        Args:
            frame (:obj:`Frame`): Open dataset frame proto.
        """
        (range_images, camera_projections, segmentation_labels, range_image_top_pose) = frame_utils.parse_range_image_and_camera_projection(frame)

        points, cp_points = frame_utils.convert_range_image_to_point_cloud(
            frame, range_images, camera_projections, range_image_top_pose, keep_polar_features=True)
        points_ri2, cp_points_ri2 = frame_utils.convert_range_image_to_point_cloud(
            frame, range_images, camera_projections, range_image_top_pose, ri_index=1, keep_polar_features=True)

        # 3d points in vehicle frame.
        points_all = np.concatenate(points, axis=0)
        points_all_ri2 = np.concatenate(points_ri2, axis=0)
        # point labels.

        points_all = np.concatenate([points_all, points_all_ri2], axis=0)
        # points_all[:,1] = (points_all[:,1] - np.min(points_all[:,1])) / (np.max(points_all[:,1]) - np.min(points_all[:,1]))

        velodyne = np.c_[points_all[:,3:6], points_all[:,1]]
        velodyne = velodyne.reshape((velodyne.shape[0] * velodyne.shape[1]))
        
        return velodyne

    
    def create_label(self, frame):
        (range_images, camera_projections, segmentation_labels, range_image_top_pose) = frame_utils.parse_range_image_and_camera_projection(frame)

        point_labels = convert_range_image_to_point_cloud_labels(
            frame, range_images, segmentation_labels)
        point_labels_ri2 = convert_range_image_to_point_cloud_labels(
            frame, range_images, segmentation_labels, ri_index=1)

        # point labels.
        point_labels_all = np.concatenate(point_labels, axis=0)
        point_labels_all_ri2 = np.concatenate(point_labels_ri2, axis=0)
        point_labels_all = np.concatenate([point_labels_all, point_labels_all_ri2], axis=0)

        labels = point_labels_all[:,1]

        return labels

    def convert_one(self, frame, dir_idx, file_idx):
        lidar_save_path = os.path.join(self.save_dir, dir_idx, 'velodyne', file_idx+'.bin')
        label_save_path = os.path.join(self.save_dir, dir_idx, 'labels', file_idx+'.label')
        point_cloud = self.create_lidar(frame)
        label = self.create_label(frame)
        point_cloud.astype(np.float32).tofile(lidar_save_path)
        label.tofile(label_save_path)
    
    def convert_all(self):
        datasets = ['training', 'validation', 'testing']

        start_idx = 0
        for dataset_type in datasets:
            print("Converting " + dataset_type + " set") 
            data_dir = os.path.join(self.load_dir, dataset_type)

            for file_name in os.listdir(data_dir):
                print(file_name)
                waymo_file_path = os.path.join(data_dir, file_name)
                dir_idx = "0" * (4 - len(str(start_idx))) + str(start_idx)

                sub_dir = os.path.join(self.save_dir, dir_idx)
                if not os.path.exists(sub_dir):
                    os.mkdir(sub_dir)
                    os.mkdir(os.path.join(sub_dir, 'velodyne'))
                    os.mkdir(os.path.join(sub_dir, 'labels'))

                data_group = tf.data.TFRecordDataset(waymo_file_path, compression_type='')
                count = 0
                for data in data_group:
                    frame = open_dataset.Frame()
                    frame.ParseFromString(bytearray(data.numpy()))
                    if frame.lasers[0].ri_return1.segmentation_label_compressed:
                        file_idx = "0" * (6 - len(str(count))) + str(count)
                        self.convert_one(frame, dir_idx, file_idx)
                        count += 1
                        

                start_idx += 1
        
        return True
                




