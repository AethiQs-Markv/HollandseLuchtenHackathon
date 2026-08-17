# Challenge 1: Colocation and Outlier Detection

## Challenge Description

This challenge focuses on automatically detecting faulty or anomalous sensors using AI techniques. By correlating sensor data with other sensors in the region and comparing against official reference measurements, you will develop methods to assign an "anomaly score" to individual sensors.

The challenge requires not only technical detection but also addressing the crucial question: **How do we communicate anomaly scores to residents in a clear and transparent manner, and what actions should they take?**

## Problem Statement

Sensor networks are subject to various types of failures and data quality issues:
- Sensor calibration drift over time
- Electronic faults or data transmission errors
- Environmental factors that affect measurement quality
- Unusual but valid atmospheric conditions

Your task is to develop an automated detection system that can:
1. Identify anomalous sensors in real-time
2. Determine confidence levels in the anomaly detection
3. Propose methods for communicating results to stakeholders
4. Suggest appropriate follow-up actions

## Approach

You can employ a combination of detection methods, including:
- **Statistical methods**: Anomaly detection based on statistical outliers, moving averages, z-scores
- **Machine Learning**: Unsupervised clustering, isolation forests, one-class SVM
- **Deep Learning**: Autoencoders, LSTM-based temporal anomaly detection, recurrent neural networks
- **Ensemble methods**: Combining multiple approaches for robust detection

## Required Data

- **Time-series data**: Calibrated and uncalibrated readings from Hollandse Luchten sensors
- **Reference measurements**: Official reference station data for validation
- **Sensor metadata**: Information about sensor locations, types, measurement communities, and intended reference stations
- **Historical quality information**: Previously identified faulty sensors, known artifacts, and periods of degraded quality
- **Regional sensor data**: Readings from neighboring sensors for correlation analysis

## Key Questions to Address

1. **Detection**: What combination of detection methods produces the most reliable results?
2. **Validation**: How do you validate your anomaly scores against reference data?
3. **Communication**: How can anomaly scores be visualized or explained to non-technical residents?
4. **Action**: What specific remediation actions should residents or operators take based on your findings?
5. **Interpretability**: Can you explain *why* a sensor was flagged as anomalous?

## Success Criteria

- Functional anomaly detection system that processes time-series data
- Validation against reference measurements showing good precision/recall balance
- Clear methodology for communicating results to residents
- Actionable recommendations for sensor maintenance or recalibration
- Documentation explaining the model and results

## Deliverables

1. **Detection Model**: Working code implementing your detection approach
2. **Validation Report**: Assessment of model performance on test data
3. **Communication Strategy**: Proposed method for presenting findings to residents
4. **Implementation Guide**: Instructions for running the system on new data
5. **Presentation**: 10-minute demonstration of your solution

## Resources

- Provided data dump with sensor readings and metadata
- Documentation of sensor types and historical issues
- Reference implementation examples
- Python libraries: pandas, scikit-learn, tensorflow/keras, or similar

## Tips

- Start with statistical methods before moving to complex deep learning
- Validate your results against reference measurements early and often
- Consider temporal patterns (time of day, seasonal effects)
- Test your anomaly scores on known faulty sensors from historical data
- Involve potential end-users (residents) in evaluating your communication strategy

---

[Back to main README](../README.md)
