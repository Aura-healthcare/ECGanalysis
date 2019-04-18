## Projet name
ECG_analysis

## Description
This repository provides an open source Python toolbox from ECG analysis:
 - ECG signal denoising
 - QRS extraction
 - HRV analysis
 - Time frequency representation
 - Classification

It relies on a melting pot of already existing Python libraries that are referenced.

The results can be displayed through Jupyter Notebook
## Usage

Use a **single-channel ECG (electrocardiogram)** as input and specify the **ECG acquisition frequency**.

### QRS extraction
We proposed different standard algorithms for QRS extraction and R-R interval computation:</br>***Algorithm name*** *, Github documentation, Research article reference*

 - **Pan Tompkin algorithm**, c-labpl/qrs_detector [[Github]](https://github.com/c-labpl/qrs_detector), A Real-Time QRS Detection Algorithm, J Pan and al. (1985) [[ref]](https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf)
 - **Hamilton algorithm**,  neuropsychology/Neurokit.py [[Github]](https://github.com/neuropsychology/NeuroKit.py), Quantitative Investigation of QRS Detection Rules Using the MIT/BIH Arrhythmia Database, P Hamilton and al. (1986) [[ref]](https://ieeexplore.ieee.org/abstract/document/4122227)
 - **GQRS algorithm**, MIT-LCP/wfdb-python [[Github]](https://github.com/MIT-LCP/wfdb-python), Physionet Documentation [[ref]](https://www.physionet.org/physiotools/wag/gqrs-1.htm)
 - **XQRS algorithm**,  MIT-LCP/wfdb-python [[Github]](https://wfdb.readthedocs.io/en/latest/processing.html#module-wfdb.processing), *variation of GQRS*
 - **Wavedet algorithm**, ,
A wavelet-based ECG delineator: evaluation on standard databases
, JP Martinez and al. (2004) [[ref]](https://ieeexplore.ieee.org/document/1275572?arnumber=1275572)
 - **Construe algorithm**, citiususc/construe [[Github]](https://github.com/citiususc/construe), On the adoption of abductive reasoning for time series interpretation, T. Teijeiro and al. (2018) [[ref]](https://www.sciencedirect.com/science/article/abs/pii/S0004370218303163?via%3Dihub)

### HRV analysis
We proposed to compute differents standard HRV indicators:

- **Time domain features:** Mean_NNI, SDNN, SDSD, NN50, pNN50, NN20, pNN20, RMSSD, Median_NN, Range_NN, CVSD, CV_NNI, Mean_HR, Max_HR, Min_HR, STD_HR
- **Geometrical domain features:** Triangular_index, TINN
- **Frequency domain features:** LF, HF, VLF, LH/HF ratio, LFnu, HFnu, Total_Power
- **Non Linear domain features:** CSI, CVI, Modified_CSI, SD1, SD2, SD1/SD2 ratio, SampEn

using the Aura-healthcare/hrvanalysis library [[Github]]()

### Time frequency representation
