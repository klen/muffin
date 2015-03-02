import datetime as dt

import peewee
from playhouse.shortcuts import model_to_dict, dict_to_model


class Serializer(object):
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_format = ' '.join([date_format, time_format])

    def convert_value(self, value):
        if isinstance(value, dt.datetime):
            return value.strftime(self.datetime_format)

        if isinstance(value, dt.date):
            return value.strftime(self.date_format)

        if isinstance(value, dt.time):
            return value.strftime(self.time_format)

        if isinstance(value, peewee.Model):
            return value.get_id()

        return value

    def clean_data(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                self.clean_data(value)
            elif isinstance(value, (list, tuple)):
                data[key] = map(self.clean_data, value)
            else:
                data[key] = self.convert_value(value)
        return data

    def serialize_object(self, obj, **kwargs):
        data = model_to_dict(obj, **kwargs)
        return self.clean_data(data)


class Deserializer(object):

    @staticmethod
    def deserialize_object(model, data):
        return dict_to_model(model, data)
