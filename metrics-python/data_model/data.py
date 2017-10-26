import pandas
import numpy
import matplotlib.pyplot as plt

'''
Data Munging

Labels
Timestamp,Build_Version,Error_Code

Since each time has multiple records, initial work will be to collapse it

knowns 2 data streams

each time has multiple records


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


if __name__ == '__main__':
    build_alpha, build_beta = '5.0007.510.011','5.0007.610.011'
    data_a = load_data_pandas('data_model/ErrorStreamSetA.csv','\t')
    
    # find len of data set and assess cardinality
    a_len, a_max, a_min = analyze_pandas(data_a)

    # aggregator
    # start building composite data set better for a 'stream' analysis
    alpha_columns = ["{1}_Error_Code_{0}".format(i,build_alpha) for i in range(a_min,a_max+1)] 
    print(alpha_columns)

    beta_columns = ["{1}_Error_Code_{0}".format(i,build_beta) for i in range(a_min,a_max)]
    #print(beta_columns)

    # take data, accumulate per second, make table double wide so index is timestamp
    data_stream = pandas.DataFrame(columns=['timestamp']+alpha_columns+beta_columns)
    #print(data_stream)
    indexes = {'timestamp':0,build_alpha:1,build_beta:(2 + a_max + (0-a_min))}
    #print(indexes)

    #print(len(data_a.index))
    #print(len(data_stream.columns.values),2 * (a_max - a_min + 1))
    #print(data_a.loc[0]['Timestamp'])
    current_timestamp = data_a.loc[0]['Timestamp']
    current_array = numpy.zeros(2 * (a_max - a_min + 1))
    for set_a_index in range(len(data_a.index)):
        if data_a.loc[set_a_index]['Timestamp'] != current_timestamp:
            data_stream = data_stream.append([dict(zip(data_stream.columns.values,
                                                        [current_timestamp]+current_array.tolist()))])
            #print(data_stream)
            # re-initialize numpy array
            current_array = numpy.zeros(2 * (a_max - a_min + 1))
            # reset timestamp
            if set_a_index < (len(data_a.index))-1:
                current_timestamp = data_a.loc[set_a_index+1]['Timestamp']
            # add first value

            if current_timestamp == "0:00:03":
                exit()
        
        # still on same timestamp, add to array
        print("Time: {2}, Build: {0}, Error Code: {1}".format(data_a.loc[set_a_index]['Build_Version'],
                                                    data_a.loc[set_a_index]['Error_Code'],
                                                    data_a.loc[set_a_index]['Timestamp']))

        current_index = indexes[data_a.loc[set_a_index]['Build_Version']] + \
            (data_a.loc[set_a_index]['Error_Code'] - a_min)
        
        current_array[current_index] += 1

        #print(current_index,current_array,data_stream.columns.values[current_index])

        
            
        

    #print(data_stream.columns.values[1])
    #print(data_stream.columns.values[indexes[build_beta]])
