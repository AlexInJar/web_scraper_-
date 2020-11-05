import numpy as np
import json


class shopping_cart(object):
    """
    Class dealing with data from the shopping cart 
    """
    def __init__(self, cart_dic_filename):
        self.data = self.read_from_file(cart_dic_filename)

    def read_from_file(self,filename, data_key = '2021_Spring_cart'):
        with open(filename) as f:
            cart_dic = json.load(f)

        return cart_dic[data_key]

    def existence_of_conflict_between_class(self, this_class, that_class):
        """
        read in two classes keys of the data
        return False if there is no conflict 
        return the time of the conflict in the form of a dictionary
        {'s1': , 's2': } 
        """
        this_dic = {this_class : {}}
        that_dic = {that_class : {}}
        for key, clas_info in self.data.items():
            if  this_class in key:
                this_dic[key[-6:]] = {'Session': clas_info['Session'], 'Days/Time':clas_info['Days/Time']}

            if that_class in key:
                that_dic[key[-6:]] = {}