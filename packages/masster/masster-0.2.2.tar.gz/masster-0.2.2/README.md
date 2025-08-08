# MASSter

**MASSter** is a comprehensive Python package for mass spectrometry data analysis, designed for metabolomics and LC-MS data processing. It provides tools for feature detection, alignment, consensus building, and interactive visualization of mass spectrometry datasets. It is designed to deal with DDA, and hides functionalities for DIA and ZTScan DIA data. 

Most core processing functions are derived from OpenMS. We use the same nomenclature and refer to their documentation for an explanation of the parameters. To a large extent, however, you should be able to use the defaults (=no parameters) when calling processing steps.

This is a poorly documented, stable branch of the development codebase in use in the Zamboni lab. Novel functionalities will be added based on need and requests.

## Features

- **Mass spectrometry data processing**: Support for multiple file formats (.wiff, .mzML, .raw, .mzpkl)
- **Feature detection and alignment**: Automated chromatographic peak detection and retention time alignment
- **Consensus feature building**: Identification of features across multiple samples
- **Interactive visualizations**: 2D plots, chromatograms, and statistical dashboards
- **Batch processing**: Process entire studies with multiple samples
- **Export capabilities**: MGF export for spectral library searches

## Installation

```bash
pip install masster
```

## Quick Start

### Basic Workflow for analyzing LC-MS study with 2-... samples

```python
import masster

# Initialize the Study object with the default folder
study = masster.Study(default_folder=r'D:\...\mylcms')

# Load data from folder with raw data, here: WIFF
study.add_folder(r'D:\...\...\...\*.wiff')

# Align maps
study.align(rt_max_diff=2.0)

# Find consensus features
study.find_consensus(min_samples=3)

# Retrieve missing data for quantification
study.fill_chrom(abs_)

# Integrate according to consensus metadata
study.integrate_chrom()

# link MS2 across the whole study and export them
study.find_ms2()
study.export_mgf()

# Save the study to .study5
study.save()
```

### Study-Level Plots

```python
# Plot features from multiple samples
study.plot_samples_2d()

# Plot consensus features
study.plot_consensus_2d()

# Plot overlaid chromatograms for specific consensus features (use their uid)
study.plot_chrom(uids=[1, 2, 3])
```


### Single Sample Processing

```python
from masster.sample import Sample

# Load a single sample (mzML, RAW, WIFF)
sample = Sample("path/to/your/file.mzML")

# Detect features
sample.find_features(chrom_peak_snr=10, noise=500, chrom_fwhm=1.0)

# Detect adducts
sample.find_adducts()

# Find MS2 spectra
sample.find_ms2()

# Save results to .sample5
sample.save()
```

Masster provides extensive plotting capabilities for data exploration and quality control:

### Single sample visualization

```python
# Plot 2D overview of MS data with detected features
sample.plot_2d(
    filename="overview_2d.html",
    show_features=True,
    show_ms2=True,
    title="MS Data Overview"
)

# Plot with feature filtering
sample.plot_2d(
    filename="features_ms2_only.html"
)

# Plot extracted ion chromatogram
sample.plot_eic(
    feature_uid=123,
    rt_tol=10,
    mz_tol=0.005
)
```

### Quality Control Plots

```python
# Plot DDA acquisition statistics
sample.plot_dda_stats(filename="dda_stats.html")

# Plot feature statistics
sample.plot_feature_stats(filename="feature_stats.html")

# Plot total ion chromatogram
sample.plot_tic(filename="tic.html")
```

### Advanced Plotting Options

```python
# Plot with Oracle annotation data
sample.plot_2d_oracle(
    oracle_folder="path/to/oracle/results",
    colorby="hg",  # Color by chemical class
    filename="annotated_features.html"
)

# Plot MS2 cycle view
sample.plot_ms2_cycle(
    cycle=100,
    filename="ms2_cycle.html",
    centroid=True
)
```

## File Format Support

- **Input formats**: .wiff, .mzML, .raw files
- **Intermediate formats**: .sample5 and .study5 (HDF5) for fast loading
- **Export formats**: .mgf, .csv
- **Visualization**: .html (interactive), .png, .svg

## Advanced Features

### Batch Processing
Use the command-line interface for processing multiple files:

```bash
python -m masster.demo.example_batch_process input_directory --recursive --dest output_directory
```

## Requirements

- Python ≥ 3.11
- Key dependencies: pandas, polars, numpy, scipy, matplotlib, bokeh, holoviews, panel
- See `pyproject.toml` for complete dependency list

## License

GNU Affero General Public License v3

## Citation

If you use Masster in your research, please cite this repository.
