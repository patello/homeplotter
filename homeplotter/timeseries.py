import datetime
import calendar

class TimeSeries():
    def __init__(self, data):
        #Only keep date and amount, even if more info is passed
        self.data=list(map(lambda x: [x[0],x[1]], data))
        self.data=sorted(self.data, key = lambda x: x[0])
        self._sum_dates()
        self._add_missing_dates()
        self.timedelta = self.data[1][0]-self.data[0][0]

    def _sum_dates(self):
        #Sum all expenses on a given date into one post
        i = 0
        data_len = len(self.data)
        while i < data_len:
            # Find all matches which has the same date as the one at index i. 
            # From https://stackoverflow.com/questions/946860/using-pythons-list-index-method-on-a-list-of-tuples-or-objects
            matches=[index for index, post  in enumerate(self.data) if post[0] == self.data[i][0]]
            #Ignore the first (last after reversing) one since it matches itself. Also reverse it since we want to delete the index without affecting the order 
            #Last tip from https://stackoverflow.com/questions/11303225/how-to-remove-multiple-indexes-from-a-list-at-the-same-time
            for j in sorted(matches[1:],reverse=True):
                #Add the amount on the current date together with the amount the matched date
                self.data[i][1] += self.data[j][1]
                del self.data[j]
            #Since the length might have change, we need to recalculate it:
            data_len = len(self.data)
            i += 1

    def _add_missing_dates(self):
        #Adds dates that are missing from the series and set that expense to zero.
        #Assumes that the series has been sorted. Only called after sorting in initialization so its ok.
        for i in range(0,len(self.data)-1):
            days_between=(self.data[i+1][0]-self.data[i][0]).days
            for j in range(1,days_between):
                self.data.append([self.data[i][0]+datetime.timedelta(j),0])
        #New dates are added to the end of the list so it needs to be sorted again
        self.data=sorted(self.data, key = lambda x: x[0])

    def get_x(self):
        return [data[0] for data in self.data]
        
    def get_y(self):
        return [data[1] for data in self.data]
    
    def accumulate(self,delta,delta_unit="Day",padding=False):
        #Loop backwards, if the iterator is not divisible by delta, add its value to cum_sum and delete it.
        #If its divisible by delta, offload cum_sum.
        if self.timedelta.days > 1:
            raise NotImplementedError("Accumulating twice is not implemented")
        
        if delta_unit == "Day":
            date_len = self.data[-1][0]-self.data[0][0]+datetime.timedelta(1)
            if padding and (date_len.days%delta) != 0:
                self.data.insert(0,[self.data[0][0]-datetime.timedelta(delta-(date_len.days%delta)),0])
                date_len = self.data[-1][0]-self.data[0][0]+datetime.timedelta(1)
            end_date = self.data[-1][0]
            stop_fun = lambda date: (delta-((end_date-date).days+1))%delta == 0
        elif delta_unit == "Week":
            if delta != 1:
                raise NotImplementedError("delta > 1 for delta_unit \"Week\" is not implemented.")
            #Need to add some logic if it is 1 week, two weeks, etc
            if padding and self.data[0][0].weekday() != 0:
                self.data.insert(0,[self.data[0][0]-datetime.timedelta(self.data[0][0].weekday()),0])
            if padding and self.data[-1][0].weekday() != 6:
                self.data.append([self.data[-1][0]+datetime.timedelta(6-self.data[-1][0].weekday()),0])
            elif self.data[-1][0].weekday() != 6:
                while len(self.data) > 0 and self.data[-1][0].weekday() != 6:
                    del self.data[-1]
            stop_fun = lambda date: date.weekday()==0
        elif delta_unit == "Month":
            if delta != 1:
                raise NotImplementedError("delta > 1 for delta_unit \"Month\" is not implemented.")
            if padding and self.data[0][0].day != 1:
                self.data.insert(0,[datetime.date(self.data[0][0].year,self.data[0][0].month,1),0])

            month = self.data[-1][0].month
            year = self.data[-1][0].year
            days_of_month = calendar.monthrange(year,month)[1]
            days_of_prev_month = calendar.monthrange(year if month > 1 else year - 1,month - 1 if month > 1 else 12)[1]

            if padding and self.data[-1][0].day != days_of_month:
                self.data.append([datetime.date(year,month,days_of_month),0])
            elif self.data[-1][0].day != days_of_prev_month and self.data[-1][0].day != days_of_month:
                while len(self.data) > 0 and self.data[-1][0].day != days_of_prev_month:
                    del self.data[-1]
            stop_fun = lambda date: date.day==1        
        elif delta_unit == "Year":
                raise NotImplementedError("delta_unit \"Year\" is not implemented.")
        else:
            raise ValueError("delta_unit must be Day/Week/Month/Year")

        if len(self.data) == 0:
            raise ValueError("Delta {delta} {delta_unit} larger than number of points in time series".format(delta=delta,delta_unit=delta_unit))

        cum_sum = 0
        for i in range(len(self.data)-1,-1,-1):
            if stop_fun(self.data[i][0]):
                self.data[i][1] += cum_sum
                cum_sum = 0
            else:
                cum_sum += self.data[i][1]
                del self.data[i]
        self.timedelta = self.data[1][0]-self.data[0][0] if len(self.data) > 1 else datetime.timedelta(-1)

    def moving_average(self,window):
        for i in range(window-1,len(self.data)):
            self.data[i][1]=sum([point[1] for point in self.data[i-window+1:i+1]])/window
        del self.data[:window-1]

    