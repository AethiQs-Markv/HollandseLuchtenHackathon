# Air Quality Data: Interpretation and Use of Low-Cost Sensors

Air quality data are not easy to interpret. Measurements are affected by factors such as weather, season, the characteristics of measuring equipment, and the way air pollution disperses. Below are several points to consider when working with air quality data and measurements from low-cost sensors.

## 1. PM2.5 and air quality

Particulate matter consists of small airborne particles that cannot be seen with the naked eye. Its composition differs by location, depending on the sources involved. PM2.5 means “Particulate Matter” with a diameter smaller than 2.5 micrometres. The smaller the particles, the deeper they can enter the lungs, which can lead to greater health impacts. Particulate matter is measured by mass, not by the number of particles. Concentrations are therefore expressed in micrograms per cubic metre (µg/m³).

Particulate matter spreads over a large area. A substantial part of the PM2.5 concentration comes from sources elsewhere in the country and abroad. This means that local differences in PM2.5 are usually relatively small. It is therefore difficult to determine the contribution of one specific local source based on PM2.5 measurements.

### Air quality and traffic emissions

Although traffic is a major source of particulate matter, it is very difficult to measure particulate emissions from a specific road. This is because a large share of traffic-related particulate matter consists of so-called secondary particulate matter. This is formed through chemical reactions of exhaust gases in the atmosphere.

Particulate matter is therefore not a suitable indicator for determining local traffic emissions. Nitrogen dioxide (NO2) is the most commonly used indicator of traffic-related air pollution. NO2 is a gas and its concentration decreases quickly with distance from the source.

This also means that a sensor located 10 metres from a road does not measure only the air pollution from that road. The measured concentration is always the result of multiple sources and atmospheric dispersion.

### Effects of weather and season

Air quality depends on weather conditions and the season. Average NO2 and PM2.5 concentrations are higher in winter and lower in summer. This is partly due to the lower mixing layer in winter. Air pollution is then dispersed through a smaller volume of air, resulting in higher concentrations. Heat and ultraviolet radiation also cause chemical reactions involving NO2 in the air, leading, among other things, to the formation of ozone.

In addition to the season, wind, temperature, precipitation and humidity can have a major influence on measured concentrations. When comparing two locations or periods, check whether weather conditions are similar. A difference between two monitoring locations may also result from differences in wind direction, wind speed or other weather conditions.

## 2. Available data sources

Several data sources can be used to compare sensor measurements or place them in a broader context.

### [GCN Tool](https://gcn-app.rivm.nl/) 

This tool shows, for each municipality, how much each source contributes to the annual average concentration of particulate matter and NO2.

### [Atlas Leefomgeving](https://www.atlasleefomgeving.nl/)

This website contains maps of the Netherlands that show modelled air pollution concentrations for any location.

### [Air quality – NO2 measurements](https://maps.amsterdam.nl/no2/)

This website provides NO2 measurements made using Palmes diffusion tubes. These measurements represent a four-week average. There are 13 monitoring periods each year.

### [Luchtmeetnet dataset](https://data.rivm.nl/data/luchtmeetnet/)

Here, you can download validated air-quality monitoring data.

Other useful data sources include weather data from the Royal Netherlands Meteorological Institute (KNMI), traffic data, road types and land use. These data can help explain differences between measurements.

## 3. Low-cost PM sensors

Most low-cost particulate matter sensors, such as the Sodaq Air, count particles that scatter light from a laser and then convert this into a mass concentration. These sensors also measure PM10, but they cannot measure this value reliably.

PM2.5 measurements are also not highly accurate and may contain errors. The actual PM2.5 concentration is often overestimated, especially during a peak in PM2.5 concentrations. Peaks of several hundred micrograms per cubic metre are often incorrect. Such concentrations are rare in the Netherlands. They may occur only during specific events, such as New Year’s Eve fireworks or a fire.

### Influence of humidity

These particulate matter sensors are sensitive to humidity. High humidity often leads to higher estimated concentrations, because the sensors interpret water droplets as particulate matter. A high measured PM2.5 concentration should therefore not automatically be interpreted as a real particulate matter peak. For unusual peaks, also check humidity levels and measurements from a nearby official monitoring station.

### Low concentrations

The lower the PM2.5 concentration, the more difficult it is for measuring equipment to measure it accurately. Relative errors are then greater. Even reference air-quality monitoring stations have difficulty measuring values close to zero. This is why negative values may occur.

It is therefore important not to look only at absolute differences. For example, a difference of 2 µg/m³ means something different when the concentration is 5 µg/m³ than when it is 50 µg/m³.

## 4. Data cleaning

Before working with sensor measurements, it is usually necessary to clean the dataset. Consider the following points.

### Check the time series

Check whether the time series is correct. Data series often miss certain hours or entire parts of a day. Also check the time zone and daylight saving time. A one-hour shift can already create a clear difference when comparing sensor data with hourly values from a monitoring station.

### Check for extreme values

Very high measurements (>100 µg/m³) that do not appear to correlate with nearby monitoring stations should be removed and reported as missing. Keep in mind that very high concentrations can occur during specific events, such as fireworks or a fire.

### Check whether sensors have become stuck

Sensors can “freeze”, causing them to report the same measurement value for weeks or months. In that case, the sensor was malfunctioning during that period. Record these measurements as missing.

Create a time-series chart straight away, as unusual peaks and periods in which a sensor has frozen are easy to identify in such a chart.

When cleaning data, do not look only at individual values, but also at patterns over time. A series of identical values, a sudden jump or a long period without variation may indicate a problem with the sensor.

### Dealing with missing values

Record incorrect measurements as `NaN` or `missing`, not as zero. Leave negative values in the dataset. Do not change them to zero and do not mark them as missing.

A value of zero means that a concentration of zero was actually measured. Missing means that no reliable measurement is available. These two situations should not be confused in the analysis.

If there is a large amount of missing data, the average is logically no longer valid. Always check how much data is used to calculate an average. Also consider whether missing data occur at random. For example, if a sensor mainly fails at night or under particular weather conditions, this may affect the average.

## 5. Other tips

### Compare sensors with reference measurements

You can compare and/or combine sensor measurements with reference measurements from official air-quality monitoring stations. This often makes the data more reliable.

Time series can be compared using, for example:

- a time-series plot;
- mean difference;
- a scatter plot;
- R².

R² alone does not tell the full story. It only shows whether the measurement series follow a similar pattern. A high R² therefore does not automatically mean that the sensor measures accurately.

For example, a sensor may consistently measure around twice as high as the official monitoring station and still have a high R².

### Use multiple sensors

Use multiple sensors and calculate averages to reduce noise. Multiple sensors also provide information about the uncertainty of a measurement. If all sensors show roughly the same trend, there is more confidence in the observed pattern.

### Temporal and spatial differences

Carefully consider the spatial scale of the study. PM2.5 spreads over a large area, and local differences will usually be small. A difference of a few micrograms per cubic metre between two sensors can therefore be difficult to interpret.

For NO2, local differences can be much greater, for example due to the distance from a busy road.

When interpreting a measurement, pay close attention to the time scale. A short peak says something different about air quality than an annual average. Therefore, decide in advance which question you want to answer with the data and which time scale is appropriate.

For health effects of air pollution, long-term, lifelong exposure is particularly relevant. Annual averages and long-term trends in residential areas are therefore used to assess health risks.

Time resolution is also important. For example, a Palmes diffusion tube provides an average over approximately four weeks, while a low-cost sensor can measure at much higher temporal resolution. These datasets therefore cannot simply be compared directly.

### Consider the research question in advance

A good analysis starts with a clear research question. The research question determines which data and analytical method are suitable. Try to identify in advance which factors may influence the results.

### A useful first analysis

For almost any dataset, a useful first step is to inspect the data visually. For example, create:

- a timeline of the measurements;
- a timeline showing multiple sensors together;
- a comparison with a nearby official monitoring station;
- a scatter plot of sensor measurements versus reference measurements;
- an overview of missing data;
- a comparison of averages over the same periods.

Do not start immediately with a complex model. A few simple charts often already reveal the main data issues and patterns.