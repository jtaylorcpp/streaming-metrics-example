import pandas
import numpy
import matplotlib.pyplot as plt

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
    alpha_columns = ["{1}_Error_Code_{0}".format(i,build_alpha) for i in range(_min,_max+1)] 
    print(alpha_columns)

    beta_columns = ["{1}_Error_Code_{0}".format(i,build_beta) for i in range(_min,_max)]
    #print(beta_columns)

    # take data, accumulate per second, make table double wide so index is timestamp
    data_stream = pandas.DataFrame(columns=['timestamp']+alpha_columns+beta_columns)
    #print(data_stream)
    indexes = {'timestamp':0,build_alpha:1,build_beta:(2 + _max + (0-_min))}
    #print(indexes)

    #print(len(data_a.index))
    #print(len(data_stream.columns.values),2 * (a_max - a_min + 1))
    #print(data_a.loc[0]['Timestamp'])
    current_timestamp = df.loc[0]['Timestamp']
    current_array = numpy.zeros(2 * (a_max - a_min + 1))
    for df_index in range(_size):
        if data_a.loc[df_index]['Timestamp'] != current_timestamp:
            data_stream = data_stream.append([dict(zip(data_stream.columns.values,
                                                    [current_timestamp]+current_array.tolist()))])
            #print(data_stream)
            # re-initialize numpy array
            current_array = numpy.zeros(2 * (a_max - a_min + 1))
            # reset timestamp
            if df_index < _size - 1:
                current_timestamp = data_a.loc[df_index + 1]['Timestamp']
            # add first value

            if current_timestamp == "0:00:03":
                exit()
        
        # still on same timestamp, add to array
        print("Time: {2}, Build: {0}, Error Code: {1}".format(data_a.loc[df_index]['Build_Version'],
                                                    data_a.loc[df_index]['Error_Code'],
                                                    data_a.loc[df_index]['Timestamp']))

        current_index = indexes[df.loc[df_index]['Build_Version']] + \
            (df.loc[df_index]['Error_Code'] - _min)

        current_array[current_index] += 1



if __name__ == '__main__':
    build_alpha, build_beta = '5.0007.510.011','5.0007.610.011'
    data_a = load_data_pandas('data_model/ErrorStreamSetA.csv','\t')
    
    # find len of data set and assess cardinality
    a_len, a_max, a_min = analyze_pandas(data_a)

    data_stream = aggregate_to_time_series(data_a,build_alpha,build_beta,a_len,a_min,a_max)
        
        

        #print(current_index,current_array,data_stream.columns.values[current_index])

        
            
        

    #print(data_stream.columns.values[1])
    #print(data_stream.columns.values[indexes[build_beta]])
