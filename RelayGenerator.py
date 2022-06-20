import numpy as np
import DataManager
from scipy.optimize import minimize

class RelayGenerator():
    def __init__(self, filepath):
        self.strokes = ['Fly', 'Back', 'Breast', 'Free']
        self.dm = DataManager.DataManager()
        self.relay_df = self.dm.clean_data(filepath)
        self.total_rows = self.relay_df.shape[0]
        self.names = self.relay_df['Name']
        self.ages = self.relay_df['Age']
        self.age_groups = self.relay_df['AgeGroup']
        self.ot_df = self.relay_df.drop(columns=['Name','Age','AgeGroup'])
        self.swimmer_data_list = self.dm.unwind_data(self.ot_df)
        self.medley_sol = self.find_medley_sol()
        self.free_sol = self.find_free_sol()

    def medley_leg_per_swimmer_constraint(self, x):
        '''Constraint that requires that each swimmer can only swim one leg
        '''
        lst = self.dm.subdivide_list(x,4)
        total_events = 0
        for sublst in lst:
            event_count = 0
            for i in range(len(sublst)):
                event_count += sublst[i]
            if event_count > 1:
                total_events += (1 - event_count)
        return total_events

    def medley_swimmer_per_leg_constraint(self, x):
        '''Constraint that requires that every leg have exactly one swimmer
        '''
        lst = self.dm.subdivide_list(x,4)
        total_swimmers = 0
        for i in range(4):
            swimmer_count = 0
            for sublst in lst:
                swimmer_count += sublst[i]
            swimmer_count -= 1
            total_swimmers += swimmer_count**2
        return total_swimmers

    def medley_age_constraint(self, x):
        '''Constraint that requires the total age to be less than 52
        '''
        return 52 - np.dot(self.dm.compress_list(x, 4), self.ages)

    def medley_objective(self, x):
        '''Medley relay function to minimize
        '''
        return np.dot(x, self.swimmer_data_list)

    def find_medley_sol(self):
        '''Finds that best medley relay given constraints
        Returns: dict, a dict that maps from swimmer name to stroke to 1 (swimming that leg) or 0 (not swimming that leg)
        '''
        #Constraints
        mspl_cons = {'type': 'eq', 'fun': self.medley_swimmer_per_leg_constraint}
        mlps_cons = {'type': 'ineq', 'fun': self.medley_leg_per_swimmer_constraint}
        age_cons = {'type': 'ineq', 'fun': self.medley_age_constraint}
        medley_cons = [mspl_cons, mlps_cons, age_cons]
        #Bounds
        medley_bounds = [[0,1] for x in range(len(self.swimmer_data_list))]
        #Estimate
        medley_est = [0 for x in range(len(self.swimmer_data_list))]
        medley_temp = minimize(self.medley_objective, medley_est, method='SLSQP', bounds=medley_bounds, constraints=medley_cons).x.round(0).tolist()
        medley_sol = self.dm.subdivide_list(medley_temp, 4)
        return {self.names[i]:{self.strokes[j]:medley_sol[i][j] for j in range(len(self.strokes))} for i in range(len(self.names))}

    def free_constraint(self, x):
        '''Constraint that requires that there be exactly 4 swimmers
        '''
        return 4 - sum(x)

    def free_age_constraint(self, x):
        '''Constraint that requires the total age to be less than 52
        '''
        return 52 - sum(x)

    def free_objective(self, x):
        '''Free relay function to minimize
        '''
        return np.dot(x, self.relay_df['Free'].tolist())


    def find_free_sol(self):
        '''Finds the best possible free relay given the constraints
        Returns: dict, a dictionary mapping from swimmer names to 1 (swimming the relay) or 0 (not swimming the relay)
        '''
        fspl_cons = {'type': 'eq', 'fun': self.free_constraint}
        free_age_cons = {'type': 'ineq', 'fun': self.free_age_constraint}
        free_cons = [fspl_cons, free_age_cons]
        # bounds
        free_bounds = [[0,1] for x in range(self.total_rows)]
        # estimate
        free_est = [0 for x in range(self.total_rows)]
        free_sol = minimize(self.free_objective,free_est, method='SLSQP', bounds=free_bounds, constraints=free_cons)
        return {self.names[i]:free_sol.x.round(0).tolist()[i] for i in range(len(self.names))}
