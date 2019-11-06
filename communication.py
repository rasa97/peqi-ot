def send_message(sender, receiver, message):
    sender.sendClassical(receiver, message)
    res = sender.recvClassical()
    assert res == b'ACK'
    
def receive_message(receiver, sender):
    msg = receiver.recvClassical()
    receiver.sendClassical(sender, b'ACK')
    return msg