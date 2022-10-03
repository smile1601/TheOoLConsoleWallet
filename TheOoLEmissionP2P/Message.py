from ToolkitBCH import getHash
import jsonpickle


class Message:

    def __init__(self, message_type, data):
        self.payload = dict()
        self.payload['messageType'] = message_type
        self.payload['data'] = data
        self.signature = getHash(self.encode(self.payload))

    def to_json(self):
        return self.__dict__

    @staticmethod
    def encode(object_to_encode):
        return jsonpickle.encode(object_to_encode, unpicklable=True)

    @staticmethod
    def decode(encoded_object):
        decoded_object = jsonpickle.decode(encoded_object)
        if Message.signature_valid(decoded_object):
            return decoded_object
        raise Exception("Message invalid!")

    @staticmethod
    def signature_valid(data):
        try:
            data_hash = getHash(Message.encode(data.payload))
            signature = data.signature
            return data_hash == signature
        except ValueError:
            raise Exception("Message invalid!")
