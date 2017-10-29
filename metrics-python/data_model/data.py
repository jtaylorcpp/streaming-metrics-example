import pandas
import numpy
import matplotlib.pyplot as plt
import seaborn as sns

'''
Data Munging

Labels
Timestamp,Build_Version,Error_Code

The stream of records comming in are intially from individual divices reporting an
    error code along with its build version.

However, since the smallest timestamp is 1 second, it seemed reasonable to aggregate all error calls into a single
    1 second time slice and use multiple records a seconf to build a counter.

This then transforms the single stream of error codes and creates a wider array (2 * number of codes) of counters
    which can be used for time-series analysis.

New Labels

Build_Version_Error_Code'1', Build_Version_Error_code'2', ...
'''

def load_data_pandas(path,delim):
    df = pandas.read_csv(path,sep=delim)
    return df


def analyze_pandas(df):
    print("Length of Data Set A: {0}".format(len(data_a)))
    idx_max = df['Error_Code'].idxmax()
    idx_min = df['Error_Code'].idxmin()
    print("Data Set A max: {0}".format(df.loc[idx_max]['Error_Code']))
    print("Data Set A min: {0}".format(df.loc[idx_min]['Error_Code']))
    return len(data_a),df.loc[idx_max]['Error_Code'],df.loc[idx_min]['Error_Code']

def aggregate_to_time_series(df,build_alpha,build_beta,_size,_min,_max):
    # aggregator
    # start building composite data set better for a 'stream' analysis
    # makes data 'double wide'
    # timestamp , build_a_error_1, ...error_2, ..., build_b_error_1, ...error_2, ...
    alpha_columns = ["{1}_Error_Code_{0}".format(i,build_alpha) for i in range(_min,_max+1)] 

    beta_columns = ["{1}_Error_Code_{0}".format(i,build_beta) for i in range(_min,_max+1)]

    indices = {'timestamp':0,build_alpha:1,build_beta:1+len(alpha_columns)}

    '''
    print(indexes)
    print(alpha_columns)
    print(beta_columns)
    '''

    # take data, accumulate per second, make table double wide so index is timestamp
    data_stream = pandas.DataFrame(columns=['timestamp']+alpha_columns+beta_columns)
    
    current_timestamp = df.loc[0]['Timestamp']
    current_array = numpy.zeros(2 * (a_max - a_min + 1))

    for df_index in range(_size):
        if df.loc[df_index]['Timestamp'] != current_timestamp: 
            data_stream.loc[len(data_stream)] = [current_timestamp]+current_array.tolist()   
            current_array = numpy.zeros(2 * (a_max - a_min + 1))
            # reset timestamp only if there is data for bucket
            # i.e. dont build bucket for timestamp 1:00:01 
            #   if there is no data to put in it
            if df_index < _size - 1:
                current_timestamp = df.loc[df_index]['Timestamp']
            ''' for debug 
            if current_timestamp == "0:00:03":
                #print(data_stream)
                return data_stream
            '''
        
        # still on same timestamp, add to array
        try:
            current_index = indices[df.loc[df_index]['Build_Version']] + \
                (df.loc[df_index]['Error_Code'] - _min)

            current_array[current_index - 1] += 1
        except Exception as e:
            # debug info for aggregation problems
            print(e)
            print("Time: {2}, Build: {0}, Error Code: {1}".format(df.loc[df_index]['Build_Version'],
                                                        df.loc[df_index]['Error_Code'],
                                                        df.loc[df_index]['Timestamp']))
            print(indices)
            print(current_index)
            print(len(current_array))
            print(indices[df.loc[df_index]['Build_Version']])
            print((df.loc[df_index]['Error_Code']))
            print(0 - (_min+1))
            
    return data_stream
'''
Heatmap

designed to manage timestamps in 'buckets' of size in seconds

allows child classes to implement plotting and ingest patterns
'''
class Heatmap(object):
    def __init__(self, bin_size=5,current_timestamp="0:00:00",threshold=1.25,threshold_bins = [1]):
        self.bin_size = bin_size
        self.current_timestamp = current_timestamp
        self.current_timestamp_int = self.timestamp_to_int(self.current_timestamp)
        self.next_timestamp_int = 0
        self.generate_next_timestamp()
        self.threshold = threshold
        self.threshold_bins = sorted(threshold_bins)

    def timestamp_to_int(self,timestamp):
        return (60*60*int(timestamp[0])) + (60*int(timestamp[2:4])) + int(timestamp[5:])

    def generate_next_timestamp(self):
        self.next_timestamp_int += self.bin_size

    def int_timestamp_to_str(self,timestamp_int):
        _sec  = timestamp_int % 60
        timestamp_int = int(timestamp_int / 60)
        _min = timestamp_int % 60
        timestamp_int = int(timestamp_int / 60)
        _hr = timestamp_int % 60
        return "{0}:{1}:{2}".format(str(_hr).zfill(1),str(_min).zfill(2),str(_sec).zfill(2))


    def ingest_record(self,record):
        pass

    def plot(self):
        pass

    def assess_thresholds(self):
        pass

'''
PercentialHeatmap

Designed to find percent increase in error codes
    i.e. build_a has 10 errors of type 5
            build_b has 100 errors of type 5
            100/10 is a tenfold increase or (1000%), which is bad

    i.e. build_a has 10 errors of type 4
            build_b has 9 errors of type 4
            9/10 is a 10 percents decrease (90% of original)
            may not be desired, but not a new 'feature'
'''

ALERT_STR = """
Alert: Mean Threshold Exceeded
    Start Timestamp: {0}
    Stop Timstamp:   {1}
    Error Code:      {2}
    Value:           {4}
    Threshold:       {3}
    Bin Size:        {5}
"""

class PercentialHeatmap(Heatmap):
    def __init__(self,df_columns=[],bin_size=5,current_timestamp="0:00:00",threshold=1.25,threshold_bins=[1]):
        super(PercentialHeatmap, self).__init__(bin_size, current_timestamp,threshold,threshold_bins)
        columns_to_use = df_columns[:int(len(df_columns)/2)]
        columns_to_build = ['_'.join(code.split('_')[1:]) for code in columns_to_use]
        #print(columns_to_build)
        self.df = pandas.DataFrame(columns=['Timestamp']+columns_to_build)

    def ingest_record(self,record):
        # make pandas dataframe row in numpy matrix
        np_record = record.as_matrix()

        ## if the heatmap df is still unititialized, add first row
        if len(self.df) == 0:
            self.df.loc[0] = [self.int_timestamp_to_str(self.current_timestamp_int)] + numpy.zeros(len(self.df.columns.values)-1).tolist()
        
        # 1. check to make sure record is within time
        if self.timestamp_to_int(np_record[0]) >= self.next_timestamp_int:
            # 1. before adding new row or timestamps, assess alerts
            self.assess_thresholds()
            # 2. update timestamps
            self.current_timestamp_int = self.next_timestamp_int
            self.generate_next_timestamp()
            # 3. add new row to df
            self.df.loc[len(self.df)] = [self.int_timestamp_to_str(self.current_timestamp_int)] + numpy.zeros(len(self.df.columns.values)-1).tolist()
        
        # 2. update current row
        #   since all records coming in are aggregations of timestamp
        #   sum average percentages (1/bin_size) * new_error_count / old_error_count

        row_size = len(self.df.loc[len(self.df) - 1]) - 1
        for idx in range(row_size):
            # if denominator is 0
            if np_record[idx + 1] == 0 or np_record[idx + 1] == 0.0:
                # if numerator is 0
                if np_record[idx + row_size + 1] == 0 or np_record[idx + row_size + 1] == 0.0:
                    # numerator and denominator are both 0 ~ call this "1"
                    self.df.loc[len(self.df)-1,self.df.columns.values[idx+1]] += (1/self.bin_size)
                else:
                    # numerator is not 0 but denominator is which is undefined
                    # numpy.nextafter(x,y) gives the smallest float number increment from x -> y
                    # https://stackoverflow.com/questions/6063755/increment-a-python-floating-point-value-by-the-smallest-possible-amount
                    # yet this results in inf which is not very helpful
                    #self.df.loc[len(self.df)-1,self.df.columns.values[idx+1]] += (1/self.bin_size) * (np_record[idx + row_size + 1]/numpy.nextafter(0,1))
                    # by comparison, adding 1 is very large as 1 ~= size of bin increase
                    #   if bin is 600 wide, then adding 1 is like having 600 error count
                    self.df.loc[len(self.df)-1,self.df.columns.values[idx+1]] += 0.05 * self.bin_size
            else:
                # both numerator and denominator are defined
                self.df.loc[len(self.df)-1,self.df.columns.values[idx+1]] += (1/self.bin_size) * (np_record[idx + row_size + 1] / np_record[idx + 1])

    def assess_thresholds(self):
        currents_thresh_bins  = self.threshold_bins
        # remove time bins to analyze f they dont exist
        while (currents_thresh_bins[-1] > len(self.df)):
            currents_thresh_bins = currents_thresh_bins[:-1]
            if len(currents_thresh_bins) == 0:
                break
        
        if len(currents_thresh_bins) > 0:
            # for each bin length, check each column  for exceeding threshold
            for column in self.df.columns.values[1:]:
                # only look at error columns
                for bin in currents_thresh_bins:
                    # assess bin number of bins in column
                    if self.df.loc[len(self.df)-bin:len(self.df)-1,column].mean() > self.threshold:
                        print(ALERT_STR.format(self.df.loc[len(self.df)-bin,"Timestamp"],self.df.loc[len(self.df)-1,'Timestamp'],
                                                column,self.threshold,self.df.loc[len(self.df)-bin:len(self.df)-1,column].mean(),
                                                bin))


        

        


        

if __name__ == '__main__':
    build_alpha, build_beta = '5.0007.510.011','5.0007.610.011'
    '''
    TEST on ErrorStreamSetA.csv
    '''
    #'''
    data_a = load_data_pandas('data_model/ErrorStreamSetA.csv','\t')
    
    # find len of data set and assess cardinality
    a_len, a_max, a_min = analyze_pandas(data_a)

    data_stream = aggregate_to_time_series(data_a,build_alpha,build_beta,a_len,a_min,a_max)
    
    print('heatmap test')
    heatmap_10m = PercentialHeatmap(df_columns=data_stream.columns.values[1:],bin_size=10,threshold_bins=[1,5,10])
    
    # 'streaming' of data
    for idx in range(len(data_stream)):
        heatmap_10m.ingest_record(data_stream.loc[idx])
    print(heatmap_10m.df.T)
    #sns.heatmap(heatmap_5s.df,annot=True)
    #'''
    '''
    TEST on ErrorStreamSetB.csv
    '''
    '''
    '''