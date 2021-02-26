import datetime

class TimeSeries():
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

    def __init__(self, data):
        #Only keep date and amount, even if more info is passed
        self.data=list(map(lambda x: [x[0],x[1]], data))
        self.data=sorted(self.data, key = lambda x: x[0])
        self._sum_dates()
        self._add_missing_dates()
    