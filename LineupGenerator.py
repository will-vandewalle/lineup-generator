import numpy as np
import pandas as pd
from RelayGenerator import RelayGenerator
import sys

class LineupGenerator():
    def __init__(self, rg, df, lanes):
        self.max_events = 3
        self.lanes = lanes # number of swimmers required in each event, i.e. lanes available
        self.rg = rg
        self.df = df
        self.names = self.df['Name']
        self.ages = self.df['Age']
        self.age_groups = self.df['AgeGroup']
        self.ot_df = self.df.drop(columns=['Name','Age','AgeGroup']) # only times df

        self.swimmers_to_no_events = {} # swimmer to event count (number of events)
        self.events_to_swimmer_names = {} # events to list of swimmers swimming them
        self.events_to_swimmer_times = {} # events to each swimmer to their time
        self.swimmers_to_event_times = {} # swimmer to each even to their time

        self.populate_swimmers_to_no_events()
        self.populate_events_to_swimmer_times()
        self.populate_events_to_swimmer_names()
        self.normalize_times()
        self.sort_lineups()
        self.event_dict_to_df()

    def populate_swimmers_to_no_events(self):
        '''Populate swimmers_to_no_events and swimmers_to_event_times
        '''
        for name in self.names:
            self.swimmers_to_event_times[name] = {}
            self.swimmers_to_no_events[name] = 0 # start at 1 because every swimmer can swim 3 individuals and 1 relay or 2 & 2
            relay_sum = int(sum(self.rg.medley_sol[name].values())) + int(self.rg.free_sol[name])
            if relay_sum == 2:
                self.swimmers_to_no_events[name] += 1
            for col in self.ot_df.columns:
                self.swimmers_to_event_times[name][col] = float(self.df.loc[self.df['Name'] == name][col]) 

    def populate_events_to_swimmer_times(self):
        '''Populate events_to_swimmer_times
        '''
        for col in self.ot_df.columns:
            self.events_to_swimmer_names[col] = []
            self.events_to_swimmer_times[col] = {}
            for name in self.names:
                self.events_to_swimmer_times[col][name] = float(self.df.loc[self.df['Name'] == name][col])

    def normalize_times(self):
        '''Normalize the times in swimmers_to_event_times and event_to_swimmer_times. The normalized times scale linearly,
        with 1 being the fastest and slower times being lower.
        '''
        for event in self.events_to_swimmer_times:
            fastest_time = min(self.events_to_swimmer_times[event].values())
            for swimmer in self.events_to_swimmer_times[event]:
                self.events_to_swimmer_times[event][swimmer] = fastest_time / self.events_to_swimmer_times[event][swimmer]
                self.swimmers_to_event_times[swimmer][event] = fastest_time / self.swimmers_to_event_times[swimmer][event]

    def populate_events_to_swimmer_names(self):
        '''Populate events_to_swimmer_names and swimmer_to_no_events. Basically start by taking fastest two
        swimmers in each event.
        '''
        for event in self.events_to_swimmer_times:
            sorted_swimmers = sorted(self.events_to_swimmer_times[event].items(), key=lambda item: item[1])
            self.events_to_swimmer_names[event] = [x[0] for x in sorted_swimmers]
            for i in range(self.lanes):
                try:
                    self.swimmers_to_no_events[sorted_swimmers[i][0]] += 1
                except IndexError:
                    pass

    def find_worst_event(self,swimmer):
        '''Returns a swimmers worst event by finding the lowest normalized score for their event.
        Parameters: swimmer, the name of the swimmer
        Returns: str, the name of the worst event for that swimmer
        '''
        event_times = []
        for event in self.events_to_swimmer_names:
            if swimmer in self.events_to_swimmer_names[event][:self.lanes]:
                event_times.append((event,self.swimmers_to_event_times[swimmer][event]))
        return sorted(event_times, key=lambda item: item[1])[0][0]

    def move_swimmer(self,swimmer):
        '''Finds a swimmers worst event and moves it down to the next fastest person.
        Parameters: swimmer, the name of the swimmer
        '''
        to_move = self.find_worst_event(swimmer)
        self.events_to_swimmer_names[to_move].remove(swimmer)
        self.swimmers_to_no_events[swimmer] -= 1
        try:
            new_swimmer = self.events_to_swimmer_names[to_move][self.lanes - 1]
            self.swimmers_to_no_events[new_swimmer] += 1
        except IndexError:
            pass

    def check_legality(self):
        '''Returns a boolean: true if the lineup is illegal, false if legal
        '''
        return True in [self.swimmers_to_no_events[x] > self.max_events for x in self.swimmers_to_no_events]

    def sort_lineups(self):
        '''Actually writes the lineups, see README for explanation of algorithm
        '''
        while self.check_legality():
            for swimmer in self.swimmers_to_no_events:
                while self.swimmers_to_no_events[swimmer] > self.max_events:
                    self.move_swimmer(swimmer)


    def event_dict_to_df(self):
        '''Takes the current format of event_to_swimmer_names and writes it into a df containing a full lineup
        '''
        df = pd.DataFrame()
        df['Name'] = self.names
        for event in self.events_to_swimmer_names:
            df[event] = ['X' if self.names.tolist()[x] in self.events_to_swimmer_names[event][:self.lanes] else np.nan for x in range(len(self.names))]
        df['Medley Relay'] = [list(self.events_to_swimmer_names.keys())[list(self.rg.medley_sol[x].values()).index(1.0)] if sum(self.rg.medley_sol[x].values()) == 1 else np.nan for x in self.names]
        df['Free Relay'] = ['X' if self.rg.free_sol[x] == 1 else np.nan for x in self.names]
        print(df)
        print(' ')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        df_filepath = sys.argv[1]
        num_lanes = int(sys.argv[2])
        if num_lanes > 3 or num_lanes < 2:
            print('Invalid lane input.') 
        else:
            rg = RelayGenerator(df_filepath)
            for age_group in rg.age_groups.unique():
                curr_age_group_df = rg.relay_df[rg.relay_df['AgeGroup'] == age_group]
                lg = LineupGenerator(rg, curr_age_group_df, num_lanes)
    else:
        print('Usage: python LineupGenerator.py <filepath_to_data> <number_of_lanes>')


