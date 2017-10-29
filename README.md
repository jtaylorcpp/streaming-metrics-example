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

    * Two step analysis may be best, aggregate then infer


### Data Format

There are two sets of data, Set A and Set B. Both have three columns:

```
Timestamp   Build_Version   Error_Code
```

#### Data Sets

##### Data Set A

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

##### Data Set B

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

## Metrics Analysis Process

After looking at the data, there are a few solution that jump out as being possible ways forward.

Many monitoring/metrics platforms take advantage of data being in time-series and then utilize things like 
counters, guages, histograms, and summaries to look and and infer behavior in the data.

With this in mind, it made sense to use the test data files, which have timestamps, to build a solution based around time-series metrics. However, the data has multiple entries for each second but a second is the smallest time bin we can make for the date as the timestamps do not have microseconds or smallers.

With seconds being the smallest bins and records coming into the system at a rate faster than 1 per second; the overall solution will be two parts: _Aggregation_ and _Analysis_

### Aggregation

The aggregation step in the system will take all records in a one second time frame and rreformat them in a way that is a bit more flexible. 

It is assumed that there are 2 pieces of information known a priori:

  * build versions

  * error codes

The aggregator then takes records in format:

```
Timestamp Build_Version Error_Code
```

And reformats them into:

```
Timestamp Build_Version1_Error_Code_1 Build_Version1_Error_Code_2 ... Build_Version2_Error_Code_1 ...
```

This allows the aggregator to take disparate and varied error records and turn them into a single record per second with each column being a counter.

The final record looks something like:

```
["0:00:00" 0 0 0 0 1 2 3 0 0 0 .... 0 2 0 0]
```

### Analysis

The analysis portion of the system now has access to records in which each error code is represented by a per build version counter.

This allows for all sorts of different time-series algorithms to be used to accomplish different types of alerts or situational awareness.

For this example, due to the visualization requirements, a heatmap seemed to be a logical way to move forward. Scatter plots or histograms could have been used but in order to make a 'read-time' visualization, the scatter plot would either be busy (up to 72 independent lines in one case) or overwhelming (18 different plots). A histogram would have also worked but watching for changes over time on a single histogram does not necessarily provide visuals for the historic data.

A heatmap, on the other hand, only has to have an entry for unique error codes as we can compare build versions and show their relation through color. This allows for each segment of the visualization to convey the relationship between builds and error codes quickly on a time-series axis while also allowing for analysis based on time buckets and not instantaneous time stamps.

#### Alerting

Since the basis for alerts in the analysis are over a time series, whcih values are alerted on are also a function of the size of the bin that has been configured.

If there is a 10000000% increase in errors in a 1 second bin, but the next 10 bins have 0 errors, is that something to worry about?

THe somewhat simple approach taken is to evaluate the mean of a series of bins. In this way, alerts with become active and then become unactive based on the amount of time passed the the stream of errors. Sustained alerts over multiple time series for the same error code would then point to a problem.

For this implementation, alerts looks like:

```
Alert: Mean Threshold Exceeded
    Start Timestamp: 0:59:00
    Stop Timstamp:   0:59:40
    Error Code:      Error_Code_3
    Value:           1.9000000000000004
    Threshold:       1.25
```

Where, in this example, the threshold is set for a 25% increase in errors (1.25) and averaged over 5 time bins where each bin is 10 seconds. 

## To Run

This example is all written in Python 3.

### Install Python 3 

#### MAC OSX

Please download and install from https://www.python.org/downloads/mac-osx/

#### Windows

Please download and install from https://www.python.org/downloads/windows/

#### Linux

Please follow this example for Ubuntu http://docs.python-guide.org/en/latest/starting/install3/linux/.

For CentOS or other distros...sorry.

### Install Pip for Python 3

Pip is currently shipped with Ptyhon 3.4+. So no need to install.

### Install Pipenv

Unsing the terminal or terminal emualtor (Windows is Git Bash), run:

```
pip3 install pipenv
```

If there is a permission error, sudo can be used:

```
sudo pip3 install pipenv
```

Pipenv is a tool that segregates Python environments in a way that allows for multiple separate environments ot exist on one machine.

### Install Project Dependencies

With pipenv installed, we can now install all of the various dependencies.

Navigate to this repo and run:

```
pipenv install
```

This will look into the Pipfile and Pipfile.lock and install the necessary dependencies in an environment to run the exmaple code.

### Run examples

By defualt, the code is configured to run against the 

