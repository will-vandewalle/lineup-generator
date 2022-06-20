import pandas as pd

'''
Class that houses all data related manipulation functions, because there are a lot unique to this project
'''
class DataManager():
    def clean_data(self, filepath):
        '''Cleans the data into a usable dataframe.
        '''
        swimmer_df = pd.read_csv(filepath)
        bins = [0, 8, 10, 12, 14, 18] # bins for age groups
        labels = ['8 and under', '9-10', '11-12', '13-14', '15-18'] # labels for age groups
        swimmer_df['AgeGroup'] = pd.cut(x=swimmer_df['Age'], bins=bins, right=True, labels=labels, ordered=True) # bin data
        swimmer_df = swimmer_df.sort_values(by=['AgeGroup', 'Name']) # organize the data
        return swimmer_df.reset_index().drop(columns=['index'])

    def compress_list(self, lst, step):
        '''Compresses a list by summing every set of size step in the list.
        Ex: [2,3,5,10,-1,2] with step = 2 --> [5,15,1]
        Parameters:
        lst, the list to compress
        step, the step size to compress by
        Returns: list, the compressed list
        '''
        compressed = []
        for i in range(0, len(lst), step):
            sublst = lst[i: i+step]
            compressed.append(sum(sublst))
        return compressed

    def subdivide_list(self, lst, step):
        '''Subdivides a list into smaller lists of length step
        Ex: [2,3,5,10,-1,2] with step = 2 --> [[2,3],[5,10],[-1,2]]
        Parameters:
        lst, the list to subdivide
        step: the length of sublists
        Returns: list, the subdivided list
        '''
        newlst = []
        for i in range(0, len(lst), step):
            sublst = lst[i:i+step]
            newlst.append(sublst)
        return newlst

    def unwind_data(self, df):
        '''Unwinds data from a df into a list, in this case a list of all swimmer times back-to-back
        Parameters:
        df, the dataframe from which to get the data
        Returns: list, the unwound data in list form
        '''
        total_rows = df.shape[0]
        data_list = []
        for i in range(total_rows):
            for j in df.iloc[i].tolist():
                data_list.append(j)
        return data_list

