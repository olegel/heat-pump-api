from can import Message

class ElsterFrame:
    WRITE = 0x0
    READ = 0x1
    RESPONSE = 0x2
    ACK = 0x3
    WRITE_ACK = 0x4
    WRITE_RESPONSE = 0x5
    SYSTEM = 0x6
    SYSTEM_RESPONSE = 0x7
    WRITE_LARGE = 0x20
    READ_LARGE = 0x21

    def __init__(self, receiver=None, elsterIndex=None, type=None, value=None, sender=0x680, msg=None, ):
        if (msg != None):
            self.initByMessage(msg)
        else:
            self.sender = sender
            self.receiver = receiver
            self.type = type
            self.elsterIndex = elsterIndex
            self.value = value

    def initByMessage(self, msg):
        self.sender = msg.arbitration_id
        data = msg.data
        self.receiver = (data[0] & 0xf0) * 8 + (data[1] & 0x0f)
        self.type = data[0] & 0x0f
        if data[2] == 0xFA:
            # extension telegram
            self.elsterIndex = ((data[3] & 0xFF) << 8) | (data[4] & 0xFF)
            if len(data) == 7:
                self.value = ((data[5] & 0xFF) << 8) | (data[6] & 0xFF)
        else:
            self.elsterIndex = data[2]
            if len(data) >= 5:
                self.value = ((data[3] & 0xFF) << 8) | (data[4] & 0xFF)

    def __str__(self):
        return "ElsterFrame [%04x -> %04x] %04x: %d (%s)" % (
            self.sender, self.receiver, self.elsterIndex, self.value, self.type
        )

    def getCanMessage(self):
        assert self.receiver <= 0x7ff
        data = []
        if self.type == ElsterFrame.READ:
            data = [0] * 5
        elif self.type == ElsterFrame.WRITE:
            data = [0] * 7

        data[0] = (self.type & 0xf) | ((self.receiver >> 3) & 0xf0)
        data[1] = self.receiver & 0x7f
        data[2] = 0xfa
        data[3] = self.elsterIndex >> 8
        data[4] = self.elsterIndex & 0xff
        if self.value != None and self.type == ElsterFrame.WRITE:
            data[5] = self.value >> 8
            data[6] = self.value & 0xff
        return Message(arbitration_id=self.sender,
                       data=data,
                       extended_id=False)