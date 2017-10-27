Streaming Metrics
=====================

# Problem Space

Design and develop a metrics/monitoring system that is capable of ingesting a stream of metrics from client applications and quickly determine if there is a significant increase in certain error codes.

## Assumptions

  1. Equal numbers of users are using both build versions

  2. Data is from a singular hour (0:00:00 - 1:00:00)

  3. The stream of metrics is stable (no lost metrics)

## Thoughts on Data

  * The smallest unit of time is 1 second
  * Multiple records come in every second

### Possible Representations

* Heatmap - diff between current and prev build is color

  * alert on time above certain threshold

* Linegraph - rates of each code comparing current and prev build

  * prolonged time above threshold triggers alert

## Metrics

  * Current thoughts on metrics consist of:
    * counter
    * gauge
    * histogram

## The Maths

  * Rate/Velocity/Slope  -> x2 - x1/ t2 - t1
    * amount of increase from last point
  * Acceleration -> v2 - v1/ t2 t1
    * how quickly the rate of the data is changing

## Data Format

There are two sets of data, Set A and Set B. Both have three columns:

```
Timestamp   Build_Version   Error_Code
```

## Data Sets

## Data Set A

```
Length of Data Set A: 14000
Data Set A max: Timestamp               1:00:00
Build_Version    5.0007.610.011
Error_Code                   15
dtype: object
Data Set A min: Timestamp               0:00:00
Build_Version    5.0007.510.011
Error_Code                  -17
dtype: object
```

## Data Set B

```
Length of Data Set B: 14000
Data Set B max error: Timestamp               1:00:00
Build_Version    5.0007.610.011
Error_Code                   14
dtype: object
Data Set B min: Timestamp               0:00:00
Build_Version    5.0007.510.011
Error_Code                   -3
dtype: object
```

## Thoughts on Streaming Metrics

