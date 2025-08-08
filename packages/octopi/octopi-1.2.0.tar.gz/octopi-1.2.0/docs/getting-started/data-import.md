# Data Import Guide

octopi leverages [copick](https://github.com/copick/copick) to provide a flexible and unified interface for accessing tomographic data, whether it's stored locally or remotely on a HPC server or on our [CryoET Data Portal](https://cryoetdataportal.czscience.com). This guide explains how to work with both data sources. If you need help creating these configuration files, detailed tutorials are available:

- [Copick Quickstart](https://copick.github.io/copick/quickstart/) - Basic configuration and setup 
- [Data Portal Tutorial](https://copick.github.io/copick/examples/tutorials/data_portal/) - Working with CryoET Data Portal


## Data Resolution

Before importing data, it's important to consider the resolution. We recommend working with tomograms at a voxel size of **10 Å (1 nm)** for optimal performance. You can downsample higher-resolution tomograms during import.

<details>
<summary><strong>💡 Example Copick Config File (config.json) </strong></summary>

The copick configuration file points to a directory that stores all the tomograms, coordinates, and segmentations in an overlay root. The config files define all the pickable objects that octopi reads to determine target segmentations and converting predicted segmentation masks to object coordinates.
```bash
{
    "name": "test",
    "description": "A test project description.",
    "version": "1.0.0",

    "pickable_objects": [
        {
            "name": "ribosome",
            "is_particle": true,
            "pdb_id": "7P6Z",
            "label": 1,
            "color": [0, 255, 0, 255],
            "radius": 150,
            "map_threshold": 0.037

        },
        {
            "name": "membrane",
            "is_particle": false,
            "label": 2,
            "color": [0, 0, 0, 255]
        }
    ],

    // Change this path to the location of sample_project
    "overlay_root": "local:///PATH/TO/EXTRACTED/PROJECT/",
    "overlay_fs_args": {
        "auto_mkdir": true
    }
}
```
</details>

## Importing Local MRC Tomograms

If you have tomograms stored locally in `*.mrc` format (e.g., from Warp, IMOD, or AreTomo), you can import them into a copick project:

```bash
octopi import-mrc-volumes \
    --mrcs-path /path/to/mrc/files \
    --config /path/to/config.json \
    --target-tomo-type denoised \
    --input-voxel-size 5 \
    --output-voxel-size 10
```

To satisfy the recommended resolution requirement, we can downsample tomograms to the desired voxel size by specifying both the original voxel size (`--input-voxel-size`) and the desired voxel size (`--output-voxel-size`). In cases where downsampling is unnecessary, simply omit the `--output-voxel-size` parameter.

### Parameter Descriptions

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--mrcs-path` | Path to directory containing MRC files | `/data/tomograms/` |
| `--config` | Path to copick config file | `/project/config.json` |
| `--target-tomo-type` | Name for the tomogram type in your copick project | `denoised`, `wbp`, `raw` |
| `--input-voxel-size` | Voxel size of your input MRC files (in Ångströms) | `5` (for 5Å data) |
| `--output-voxel-size` | (Optional) Target voxel size after downsampling | `10` (downsample to 10Å) |

## Downloading from the CryoET Data-Portal

The [CryoET Data Portal](https://cryoetdataportal.czscience.com) provides access to thousands of annotated tomograms. Octopi can work with this data in two ways:

### 1. Direct Portal Access

You can train models directly using data from the portal without downloading:

```bash
octopi train-model \
    --config portal_config.json \
    --datasetID 10445 \
    --voxel-size 10
```

### 2. Local Download and Processing

For larger datasets or when running multiple experiments, it is recommended to download the data first:

```bash
octopi download-dataportal \
    --config /path/to/config.json \
    --datasetID 10445 \
    --overlay-path /path/to/saved/zarrs \
    --input-voxel-size 5 --output-voxel-size 10 \
    --dataportal-name wbp --target-tomo-type wbp
```

Similar to local MRC import, you can downsample portal data by specifying both `--input-voxel-size` and `--output-voxel-size` parameters.  To find available tomogram names for a dataset available on the portal, use:

```bash
copick browse -ds <datasetID>
```

This will save these tomograms locally under the `--target-tomo-type` flag.

## Next Steps

Once your data is imported, you can:

- [Try the Quick Start](quickstart.md) - Complete end-to-end workflow example
- [Prepare Training Data](../user-guide/labels.md) - Set up your particle annotations
- [Start Training Models](../user-guide/training.md) - Train custom 3D U-Net models
- [Run Inference](../user-guide/inference.md) - Apply trained models to new data