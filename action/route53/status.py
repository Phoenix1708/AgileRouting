class Status(object):
    def __init__(self, route53connection, change_dict):
        self.route53connection = route53connection
        for key in change_dict:
            if key == 'Id':
                self.__setattr__(key.lower(),
                                 change_dict[key].replace('/change/', ''))
            else:
                self.__setattr__(key.lower(), change_dict[key])

    def update(self):
        """ Update the status of this request."""
        status = self.route53connection\
            .get_change(self.id)['GetChangeResponse']['ChangeInfo']['Status']
        self.status = status
        return status

    def __repr__(self):
        return '<Status:%s>' % self.status
