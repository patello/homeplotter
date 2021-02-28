import datetime

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
    
    def accumulate(self,delta,forward=False,padding=False):
        #Loop backwards, if the iterator is not divisible by delta, add its value to cum_sum and delete it.
        #If its divisible by delta, offload cum_sum.

        if padding and (len(self.data)%delta) != 0:
            cur_date = self.data[-1 if forward else 0][0]
            data_len = len(self.data)
            for i in range(1,(delta-(data_len%delta))+1):
                if forward:
                    self.data.append([cur_date+self.timedelta*i,0])
                else:
                    self.data.insert(0,[cur_date-self.timedelta*i,0])

        if forward:
            i_offset = 0
        else:
            i_offset = delta-(len(self.data)%delta)

        if forward and (len(self.data)%delta) != 0:
            del self.data[-(len(self.data)%delta):]

        cum_sum = 0
        for i in range(len(self.data)-1,-1,-1):
            if (i+i_offset) % delta == 0:
                self.data[i][1] += cum_sum
                cum_sum = 0
            else:
                cum_sum += self.data[i][1]
                del self.data[i]
            
        self.timedelta = datetime.timedelta(delta)

    def moving_average(self,window):
        for i in range(window-1,len(self.data)):
            self.data[i][1]=sum([point[1] for point in self.data[i-window+1:i+1]])/window
        del self.data[:window-1]

    