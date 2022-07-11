# Convert waymo open dataset 3D Segmentation format to SemanticKITTI format

Convert waymo open dataset 3D segmentation format to SemanticKITTI format.

Run the script:
```
python convert.py --load_dir /path/to/original/waymo_format --save_dir /path/to/new/semantickitti_format
```

```
nohup python convert.py --load_dir /path/to/original/waymo_format  --save_dir /path/to/new/semantickitti_format >converter.log &
```

Dataset dir:

```
── /path/to/original/waymo_format
  │-- training
  │   │-- segment-10017090168044687777_6380_000_6400_000_with_camera_labels.tfrecord
  │   |-- segment-10023947602400723454_1120_000_1140_000_with_camera_labels.tfrecord
  │   |-- ...
  |-- validation
  |   |-- segment-10203656353524179475_7625_000_7645_000_with_camera_labels.tfrecord
  |   |-- segment-1024360143612057520_3580_000_3600_000_with_camera_labels.tfrecord
  │   |-- ...
  `-- testing
      │-- segment-10084636266401282188_1120_000_1140_000_with_camera_labels.tfrecord
      │-- segment-10149575340910243572_2720_000_2740_000_with_camera_labels.tfrecord
      │-- ...
```


```
── /path/to/new/semantickitti_format
  │-- sequences
  │   |-- 0000
  │   |   |-- labels
  │   |   |   |-- 000000.label
  │   |   |   |-- 000001.label
  │   |   |   |-- ...
  │   |   |-- velodyne
  │   |   |   |-- 000000.bin
  │   |   |   |-- 000001.bin
  │   |   |   |-- ...
  │   |-- 0001
  │   |-- ...
```

