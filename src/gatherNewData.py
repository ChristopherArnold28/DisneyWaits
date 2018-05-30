




def create_new_data(old_data):
    #get unique rides from training data
    rides = old_data.Name.unique()
    #extract first row just to have all the important catgories

    #populate time from park open to park close every 15 minutes
