import pandas as pd
from components import Warehouse, Forklift

class Simulation:
    def __init__(self, warehouse_x_dim, warehouse_y_dim, n_forklifts, forklift_job_lists):
        if len(forklift_job_lists) < n_forklifts:
            raise "Need at least as many jobs as forklifts"
        self.n_forklifts = n_forklifts
        self.forklift_start_positions = [[0, 0] for k in range(n_forklifts)]
        self.n_jobs = len(forklift_job_lists)
        self.warehouse = Warehouse(warehouse_x_dim, warehouse_y_dim)
        self.forklift_names=[]
        self.forklift_job_lists=forklift_job_lists
        for k in range(self.n_forklifts):
            self.__setattr__('Forklift'+str(k), Forklift(self.forklift_start_positions[k], forklift_job_lists[k]))
            self.forklift_names.append('Forklift'+str(k))

    def run(self, outputfile):
        output = pd.DataFrame()
        t = 0
        job_ticker = self.n_forklifts
        for name in self.forklift_names:
            forklift = self.__getattribute__(name)
            forklift.update_travel_time(t)
        while job_ticker < len(self.forklift_job_lists) + self.n_forklifts:
            for name in self.forklift_names:
                forklift = self.__getattribute__(name)
                if forklift.next_update_time <= t:
                    if (forklift.status == 'traveling') or (forklift.status == 'waiting'):
                        if self.warehouse.__getattribute__(str(forklift.position)).occupied == 0:
                            self.warehouse.__getattribute__(str(forklift.position)).occupied = 1
                            forklift.update_pick_up_time(t)
                        else:
                            forklift.status = 'waiting'
                    elif forklift.status == 'picking':
                        self.warehouse.__getattribute__(str(forklift.position)).occupied = 0
                        forklift.update_travel_time(t)
                        if forklift.status == 'complete':
                            print("Job completed!")
                            if job_ticker < len(self.forklift_job_lists):
                                forklift.job_list = self.forklift_job_lists[job_ticker]
                                forklift.job_number = 0
                                forklift.update_travel_time(t)
                            job_ticker += 1
                output = output.append([[t, name, forklift.position, forklift.status]])
                print("Time: ", t, " Jobs Completed: ", job_ticker - self.n_forklifts, " Total Jobs: ", len(self.forklift_job_lists))
            t += 1
        output.columns = ['time', 'name', 'current_destination', 'status']
        output.to_csv(outputfile, index=False)
        print("simulation complete")