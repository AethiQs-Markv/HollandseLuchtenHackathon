# Challenge 2: Geographic Hotspot Determination with Visual Wind Roses Over Time

## Challenge Description

This challenge leverages the power of visual analysis and unsupervised learning to identify geographic pollution hotspots over time. Previous analyses have shown that pollution roses (wind roses colored by pollution concentration) provide clear and intuitive insights into air quality patterns.

However, generating and analyzing these visualizations is time-consuming and dependent on analysis granularity. **Your challenge is to create an AI system that automatically analyzes sequences of pollution roses over time to detect unusual hotspots and support source identification.**

## Problem Statement

Pollution roses are powerful tools for understanding local air quality patterns in relation to wind direction and speed. By visualizing these roses over extended time periods on a geographic map, you essentially create a "video" or time-series of frames showing how pollution patterns evolve.

Your task is to:
1. Process temporal sequences of pollution roses as visual data
2. Apply unsupervised learning to identify anomalous hotspots
3. Locate these hotspots geographically on a map
4. Provide insights into potential pollution sources
5. Scale analysis to much longer periods than manual approaches allow

## Approach

Modern AI architectures designed for visual encoding can analyze pollution rose sequences to identify patterns:
- **Computer Vision**: Convolutional neural networks (CNNs) for spatial pattern recognition
- **Unsupervised Learning**: Clustering algorithms (K-means, DBSCAN) on visual features
- **Autoencoders**: Learn normal pollution rose patterns and flag deviations
- **Temporal Analysis**: Recurrent neural networks (RNNs) or 3D CNNs for sequence analysis
- **Feature Extraction**: Custom metrics derived from wind rose properties (direction concentration, intensity patterns)

## Required Data

You have two options (or a combination):

1. **Pre-prepared pollution roses**: Pre-computed pollution roses for different time periods
   - Varies temporal granularity (hourly, daily, weekly aggregations)
   - Pre-rendered as images or data representations

2. **Raw sensor data + generation toolkit**: 
   - Sensor measurements with wind direction and speed data
   - Code and formulas to generate pollution roses
   - Allows experimentation with different timeframe lengths

**Additional data**:
- Geographic coordinates of sensor locations
- Map data for hotspot visualization
- Reference data for validation (if available)

## Key Questions to Address

1. **Temporal Granularity**: How does the timeframe length (e.g., hourly vs. daily aggregation) affect hotspot detection?
2. **Visual Encoding**: What visual features best indicate anomalous pollution patterns?
3. **Unsupervised Learning**: Which clustering or anomaly detection methods work best on visual wind rose data?
4. **Geographic Mapping**: How do you translate detected anomalies back to geographic locations and source regions?
5. **Interpretability**: Can you explain *what* makes a hotspot anomalous? Is it a new pollution source, wind pattern shift, or other factors?
6. **Scaling**: How well does your approach scale to months or years of data?

## Success Criteria

- Functional system that processes temporal sequences of pollution data
- Visual or geographic output showing detected hotspots
- Validation that detected hotspots correspond to known pollution events or sources
- Ability to analyze extended time periods (weeks to months) efficiently
- Clear interpretation of what constitutes an anomaly

## Deliverables

1. **Visual Analysis System**: Code implementing your hotspot detection approach
2. **Hotspot Visualizations**: Maps showing detected anomalous hotspots with confidence levels
3. **Temporal Analysis**: Demonstration of how patterns evolve over your chosen time period
4. **Source Investigation**: Proposed mechanisms for identifying potential pollution sources
5. **Performance Report**: Analysis of different temporal granularities and their effectiveness
6. **Presentation**: 10-minute demonstration with interactive visualizations

## Resources

- Provided data dump with sensor measurements and wind direction/speed data
- Python libraries: matplotlib, folium, scikit-learn, tensorflow/keras, opencv
- Visualization libraries: plotly, geopandas for geographic visualization
- Pollution rose generation libraries (if needed)
- Optional: Pre-rendered pollution rose images if visual-only approach preferred

## Tips

- Start by visualizing a single time-series of pollution roses to understand the data
- Experiment with different temporal granularities to find the optimal balance
- Use clustering algorithms as a baseline before moving to neural networks
- Compare detected hotspots against known pollution events (if available)
- Consider combining spatial (CNN) and temporal (RNN) components
- Create clear visualizations showing "normal" vs. "anomalous" patterns
- Test whether your system can identify known pollution sources

---

[Back to main README](../README.md)
