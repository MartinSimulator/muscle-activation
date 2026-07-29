# Processing Strategies for Surface Electromyography in Machine Learning-Based Exercise Classification

Surface electromyography (sEMG) captures the temporal and spatial summation of motor unit action potentials (MUAPs) generated during skeletal muscle contraction. Raw sEMG signals acquired during dynamic resistance exercises—such as the standing barbell curl, hammer curl, and preacher curl—are inherently non-stationary, complex, and highly susceptible to ambient electrical noise, motion artifacts, and physiological interference.

To train robust machine learning models capable of classifying specific exercise variations executed at high loads (such as 75% of one-repetition maximum [1RM]), raw microvolt-level potential differences must undergo a sequence of digital signal conditioning, temporal segmentation, domain-specific feature extraction, and appropriate amplitude normalization.

## Standardized sEMG Preprocessing Architecture

Raw sEMG signals recorded during high-load resistance training exhibit amplitudes ranging from $50\,\mu\mathrm{V}$ to several millivolts, with dominant signal energy concentrated between 10 Hz and 500 Hz. Transforming these raw signals into structured numerical inputs requires a sequential filtering pipeline compliant with international recommendations, such as the Surface Electromyography for the Non-Invasive Assessment of Muscles (SENIAM) guidelines.

The preprocessing architecture begins with digital filtering to isolate true physiological excitation from mechanical and electromagnetic noise. Attenuating low-frequency artifacts caused by electrode-skin interface displacement, cable sway, and gross body movement during repetitive lifting is achieved using a 4th-order or 5th-order zero-lag (bi-directional) Butterworth band-pass filter with cutoff frequencies set at 20 Hz and 450 Hz. The 20 Hz high-pass boundary eliminates baseline wander and motion artifacts without stripping significant MUAP spectral energy. The 450 Hz low-pass boundary attenuates high-frequency thermal noise and prevents aliasing prior to feature calculation. Employing zero-lag forward-backward filtering suppresses phase distortion, preserving the exact temporal alignment of muscle activation onsets and burst envelopes.

Powerline interference, arising from ambient 50 Hz or 60 Hz electromagnetic radiation, presents a dominant narrow-band artifact. A zero-phase notch filter (or a narrow band-stop infinite impulse response filter) centered at 50/60 Hz with a high quality factor ($Q \ge 30$) isolates and suppresses powerline hum while preserving adjacent physiological frequency components. Following spectral filtering, high-intensity dynamic movements performed at 75% 1RM require transient artifact removal. Mechanical shocks or electrode shifting during heavy repetitions can induce transient voltage spikes. Preprocessing protocols apply sliding-window thresholding to identify and exclude signal segments exceeding $\pm 3$ to $\pm 5$ standard deviations from the trial mean before downstream feature computation.

## Signal Segmentation and Windowing Protocols

Machine learning algorithms require static feature vectors calculated over localized temporal intervals rather than continuous unbounded time series. Consequently, filtered sEMG streams must be segmented into discrete temporal windows.

Signal segmentation employs either disjoint (adjacent) windows or overlapping sliding windows. Overlapping sliding windows are widely adopted in pattern recognition frameworks because they maintain temporal continuity across movement phases and expand the total sample size available for model training. A standard window length ($W$) ranges between 128 ms and 256 ms, paired with an overlap increment ($S$) of 25% to 50% (such as a 256 ms window sliding in 64 ms or 128 ms steps). The overlap percentage is defined mathematically as:

$$
\text{Overlap Ratio (\%)} = \left(1 - \frac{S}{W}\right) \times 100
$$

For real-time classification and feedback, total algorithmic latency—encompassing window duration and feature calculation—must remain below 300 ms to satisfy human-computer interaction constraints. In offline classification tasks focusing on full repetition cycles at 75% 1RM, researchers segment signals into whole-repetition windows or distinct concentric and eccentric contraction phases to evaluate activation dynamics across the complete range of motion.

## Mathematical Feature Extraction Framework

Extracting discriminative features projects raw time-series matrices into a lower-dimensional feature space, isolating biomechanical activation differences from stochastic noise. Features are categorized across Time Domain (TD), Frequency Domain (FD), and Time-Frequency Domain (TFD) representations.

### Time-Domain Metrics

Time-domain features compute statistical metrics directly from amplitude time series without transformation, combining high computational efficiency with strong classification performance.

Mean Absolute Value (MAV) measures the average absolute amplitude within a window of $N$ samples, acting as an indicator of overall neural drive:

$$
\mathrm{MAV} = \frac{1}{N} \sum_{i=1}^{N} \lvert x_i \rvert
$$

Root Mean Square (RMS) reflects the square root of the average power, correlating with physiological motor unit recruitment and muscle force output:

$$
\mathrm{RMS} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} x_i^2}
$$

Waveform Length (WL) calculates the cumulative length of the amplitude trajectory over the window, capturing signal complexity, amplitude, and frequency variations simultaneously:

$$
\mathrm{WL} = \sum_{i=1}^{N-1} \lvert x_{i+1} - x_i \rvert
$$

Zero Crossing (ZC) counts the occurrences where the signal crosses the zero-voltage axis, serving as a time-domain proxy for dominant frequency. A voltage threshold ($\epsilon$) is incorporated to prevent low-amplitude noise from triggering false counts:

$$
\mathrm{ZC} = \sum_{i=1}^{N-1} f(x_i, x_{i+1}), \quad \text{where }
f(a,b) = \begin{cases}
  1 & \text{if } (a \cdot b < 0) \text{ and } \lvert a - b \rvert \ge \epsilon \\
  0 & \text{otherwise}
\end{cases}
$$

Slope Sign Change (SSC) tallies the instances where the signal slope changes sign across successive points, tracking spectral distribution properties in the time domain:

$$
\mathrm{SSC} = \sum_{i=2}^{N-1} g(x_i, x_{i-1}, x_{i+1}), \quad \text{where }
g(a,b,c) = \begin{cases}
  1 & \text{if } (a - b)(a - c) \ge \epsilon \\
  0 & \text{otherwise}
\end{cases}
$$

### Frequency-Domain Metrics

Frequency-domain metrics are derived from the Power Spectral Density (PSD) function, $P(f)$, typically estimated using Discrete Fourier Transforms (DFT). These features capture spectral shifts associated with motor unit firing rates and physiological fatigue during heavy loading.

Mean Frequency (MNF) represents the power-spectrum-weighted average frequency:

$$
\mathrm{MNF} = \frac{\sum_{j=1}^{M} f_j P(f_j)}{\sum_{j=1}^{M} P(f_j)}
$$

where $M$ denotes the total number of frequency bins, $f_j$ is the frequency at bin $j$, and $P(f_j)$ is the power spectral density.

Median Frequency (MDF) divides the total spectral power into two equal halves:

$$
\sum_{j=1}^{\mathrm{MDF}} P(f_j) = \sum_{j=\mathrm{MDF}}^{M} P(f_j) = \frac{1}{2} \sum_{j=1}^{M} P(f_j)
$$

During dynamic resistance exercise at 75% 1RM, localized muscular fatigue reduces muscle fiber conduction velocity, causing $MNF$ and $MDF$ to shift toward lower frequencies across successive repetitions. Combining frequency metrics with time-domain amplitudes ensures that machine learning models remain resilient against fatigue-induced spectral shifts when classifying exercise types.

### Time-Frequency Domain Transformations

Because dynamic contraction cycles alter muscle fiber length, geometry, and sensor alignment relative to active motor units, sEMG signals acquired during resistance training exhibit non-stationary properties. Wavelet Packet Transforms (WPT) and Continuous Wavelet Transforms (CWT) decompose signals into localized time-frequency sub-bands. Calculating energy or variance across discrete wavelet coefficients yields stable features that remain robust under non-stationary dynamic conditions.

| **Feature Name** | **Feature Domain** | **Mathematical Expression** | **Target Physiological Characteristic** | **Computational Complexity** |
| --- | --- | --- | --- | --- |
| **Mean Absolute Value (MAV)** | Time | \(\mathrm{MAV} = \frac{1}{N} \sum_{i=1}^{N} \lvert x_i \rvert\) | Activation amplitude and neural drive intensity | Very Low |
| **Root Mean Square (RMS)** | Time | \(\mathrm{RMS} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} x_i^2}\) | Signal power and motor unit recruitment | Very Low |
| **Waveform Length (WL)** | Time | \(\mathrm{WL} = \sum_{i=1}^{N-1} \lvert x_{i+1} - x_i \rvert\) | Signal complexity and cumulative amplitude variation | Low |
| **Zero Crossing (ZC)** | Time | Count of sign changes exceeding noise threshold \(\epsilon\) | Dominant spectral frequency proxy | Low |
| **Slope Sign Change (SSC)** | Time | Count of slope inflection points exceeding threshold \(\epsilon\) | Frequency spectrum distribution proxy | Low |
| **Mean Frequency (MNF)** | Frequency | \(\mathrm{MNF} = \frac{\sum f_j P(f_j)}{\sum P(f_j)}\) | Spectral centroid and fiber conduction velocity | Moderate |
| **Median Frequency (MDF)** | Frequency | Frequency splitting PSD area into equal energy halves | Fatigue progression and motor unit shift | Moderate |
| **Wavelet Packet Energy** | Time-Frequency | \(E_{\mathrm{sub}} = \sum \lvert C_{i,j} \rvert^2\) | Non-stationary sub-band power distribution | High |

## Normalization Strategies for Heavy Dynamic Resistance Tasks

Amplitude normalization converts raw microvolt values into standardized relative percentages, enabling valid comparisons between different exercises, muscle groups, experimental sessions, and individuals. Unnormalized sEMG amplitudes are dictated by confounding non-physiological variables, including subcutaneous fat thickness, skin-electrode impedance, local temperature, and slight shifts in sensor placement.

The traditional normalization approach scales dynamic sEMG amplitudes against the peak RMS value recorded during a Maximal Voluntary Isometric Contraction (% MVIC). However, applying isometric MVIC baselines to dynamic resistance training at 75% 1RM introduces methodological limitations.

Isometric tests evaluate muscle activation at a static joint angle, whereas dynamic bicep flexions involve continuously changing muscle lengths, moment arms, and muscle-tendon architecture. MVIC normalization in dynamic tasks frequently yields high inter-subject coefficients of variation ($CV \ge 55\%$) and can produce activation values exceeding 100% of MVIC due to dynamic stretch-shortening dynamics or inertial acceleration peaks.

To overcome these constraints, researchers utilize **Peak Dynamic EMG** or **Mean Dynamic EMG** normalization. Scaling feature matrices against the maximum or mean dynamic amplitude recorded during the target exercise task significantly reduces inter-subject variability ($CV \approx 12\% - 30\%$) and provides stable input distributions for pattern recognition models.

Designing normalization protocols for bicep curl variations at 75% 1RM requires accounting for exercise-specific biomechanical parameters:

- **Standing Barbell Curl:** Exercises both the long and short heads of the biceps brachii with the forearm fully supinated. The shoulder remains in a neutral position, placing the peak external torque demand near 90 degrees of elbow flexion.
- **Hammer Curl:** Executed with a neutral (semi-pronated) forearm position, shifting mechanical advantage toward the brachioradialis and brachialis while reducing biceps brachii contribution. Normalizing hammer curl activation using a fully supinated isometric MVIC overestimates relative biceps brachii effort.
- **Preacher Curl:** Positions the upper arm on a sloped pad, maintaining approximately 45 degrees of shoulder flexion. This position shortens the biceps brachii (inducing active insufficiency) and shifts peak torque to the initial phase of elbow flexion.

Using a task-specific dynamic peak normalization strategy—where sEMG features for each movement variation are scaled relative to the maximum dynamic peak recorded across the 75% 1RM repetitions—preserves movement-specific recruitment signatures while standardizing feature ranges for classifier training.

| **Normalization Method** | **Reference Baseline** | **Inter-Subject Variability (CV)** | **Primary Advantages** | **Major Disadvantages in Dynamic ML** |
| --- | --- | --- | --- | --- |
| **Maximal Voluntary Isometric Contraction (MVIC)** | Peak RMS from static maximal manual resistance test | High (\(55\% - 77\%\)) | Reflects activation relative to absolute maximal isometric capacity | High inter-subject variance; angle-dependent; dynamic activation often exceeds 100% |
| **Peak Dynamic EMG (% Peak Dynamic)** | Maximum peak RMS recorded during dynamic movement trial | Low to Moderate (\(19\% - 35\%\)) | Lower coefficient of variation; accommodates dynamic joint angle changes | Suppresses baseline absolute force production differences across subjects |
| **Mean Dynamic EMG (% Mean Dynamic)** | Average RMS calculated across concentric movement phase | Low (\(12\% - 25\%\)) | High repeatability across multi-repetition exercise sets | Highly sensitive to repetition tempo variations and joint pause durations |
| **Submaximal Task Reference** | Fixed submaximal load baseline (e.g., set percentage of 1RM) | Low to Moderate (\(15\% - 30\%\)) | High test-retest reliability across multi-day collection sessions | Requires dedicated standardized calibration trials for each subject |

## Machine Learning Classification Architecture and Data Integrity

Transforming processed sEMG feature sets into accurate exercise classifiers requires structuring feature vectors, applying dimensionality reduction, and enforcing strict validation splits to prevent data leakage.

### Dimensionality Reduction and Feature Selection

When capturing multi-channel sEMG across targeted muscles (such as the biceps brachii long head, short head, brachioradialis, and anterior deltoid), combining time-, frequency-, and time-frequency-domain metrics creates high-dimensional feature matrices. High dimensionality increases computational overhead and risks model overfitting.

Dimensionality reduction is routinely managed using Principal Component Analysis (PCA) or Recursive Feature Elimination (RFE). PCA projects multi-domain metrics onto orthogonal linear components, retaining 95% to 99% of total variance while compressing feature dimension size. Alternatively, RFE iteratively evaluates feature subsets using tree-based classifiers to prune redundant features, consistently identifying Waveform Length ($WL$) and Mean Absolute Value ($MAV$) as high-ranking metrics for myoelectric pattern recognition.

### Data Leakage Control in Cross-Validation Protocols

A common flaw in sEMG pattern recognition studies is the random partitioning of overlapping sliding windows into training and testing datasets. Because adjacent overlapping windows originate from continuous time-series recordings, they share significant temporal autocorrelation. Random window assignment allows the model to memorize temporal neighbors, causing severe data leakage and artificially inflated validation metrics.

To ensure real-world model generalizability, validation protocols must implement a **Subject-Wise Split** (such as `GroupKFold` cross-validation grouped strictly by Participant ID). Under this strategy, all data trials from a given subject are isolated exclusively within either the training set or the testing set. This prevents classifiers from fitting subject-specific electrical noise or skin impedance artifacts, forcing the model to learn underlying biomechanical activation patterns common across exercise variations.

### Machine Learning Classifier Paradigms

Tree-based ensembles, such as XGBoost and Random Forest, handle tabular multi-domain feature vectors effectively, demonstrating resilience against variations in feature scale. Support Vector Machines (SVM) utilizing Radial Basis Function (RBF) kernels construct non-linear decision boundaries to separate subtle activation differences between similar movement variations. Modern deep learning frameworks process raw two-dimensional time-frequency spectrograms (derived via Continuous Wavelet Transforms or Short-Time Fourier Transforms) using Convolutional Neural Networks (CNN) or Vision Transformers (ViT), automatically learning spatial-temporal muscle activation patterns without requiring manual feature engineering.

## End-to-End Methodological Workflow for Exercise Activation Classification

Executing a end-to-end sEMG processing pipeline to classify muscle activation across bicep curl variations at 75% 1RM follows a defined, step-by-step methodology:

First, sEMG signals are recorded at a sampling rate of at least 1000 Hz using surface electrodes positioned on the biceps brachii (long and short heads) and brachioradialis, adhering to SENIAM placement standards.

Second, raw potential values undergo digital conditioning using a 4th-order zero-lag Butterworth band-pass filter (20–450 Hz) combined with a 50/60 Hz notch filter to remove low-frequency baseline drift, motion artifacts, and powerline interference.

Third, the clean continuous sEMG data stream is segmented using a sliding window strategy with a frame length of 256 ms and a 50% overlap increment (128 ms step size).

Fourth, amplitude features within each window are normalized using the Peak Dynamic EMG value obtained during maximal dynamic effort repetitions to minimize inter-subject variability while preserving movement dynamics.

Fifth, a multi-domain feature vector is constructed for each window, extracting Mean Absolute Value ($MAV$), Root Mean Square ($RMS$), Waveform Length ($WL$), Zero Crossings ($ZC$), Slope Sign Changes ($SSC$), and Wavelet Packet Energy coefficients.

Sixth, feature selection algorithms (such as RFE or PCA) prune redundant metrics to optimize feature space dimensionality.

Finally, the engineered feature matrix is fed into a machine learning classifier—such as XGBoost or an RBF-Kernel SVM—evaluated via a subject-wise `GroupKFold` cross-validation architecture to ensure robust generalization across unseen individuals.
