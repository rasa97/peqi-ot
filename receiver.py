from cqc.pythonLib import CQCConnection, qubit
from communication import send_message, receive_message

import random

class Receiver(object):
    def __init__(self, decision_bit, name="Bob"):
        self.cqc = None
        self.name = name

        self.N = 32

        self.raw_key = []
        self.basis_list = []
        self.sifted_basis = []

        self.decision_bit = decision_bit
        self.good_index = None

    def receive_qubits(self, sender):
        
            print("Receiving {} qubits...".format(self.N))
            for _ in range(0, self.N):
                # Receive qubit from Alice
                q = self.cqc.recvQubit() 

                # Choose a random basis
                chosen_basis = random.randint(0, 1)
                self.basis_list.append(chosen_basis)
                if chosen_basis == 1:
                    q.H()

                # Retrieve key bit
                k = q.measure()
                self.raw_key.append(k)

    def receive_basis_information(self, sender):
        msg = receive_message(self.cqc, sender)
        return list(msg)

    def perform_basis_sift(self, basis_list):
        good = []
        bad = []

        for i in range(0, len(basis_list)):
            if basis_list[i] == self.basis_list[i]:
                good.append(i)
            else:
                bad.append(i)

        self.good_index = random.randint(0,1)
        if self.good_index:
            return bad, good
        return good, bad 

    def send_sets(self, sender, sets):
        send_message(self.cqc, sender, sets[0])
        send_message(self.cqc, sender, sets[1])

    def receive_parities_addresses(self, sets, sender):
        parities = [[], []]
        parities[0] = [int(x) for x in receive_message(self.cqc, sender)]
        parities[1] = [int(x) for x in receive_message(self.cqc, sender)]

        parity = 0
        for i in range(0, len(parities[self.good_index])):
            parity = (parity + sets[self.good_index][parities[self.good_index][i]]) % 2

        return parity

    def get_chosen_bit(self, sender, good_set_parity):
        send_message(self.cqc, sender, self.good_index == self.decision_bit)
        parities = []
        parities.append(int.from_bytes(receive_message(self.cqc, sender), 'little'))
        parities.append(int.from_bytes(receive_message(self.cqc, sender), 'little'))
        retrieved_bit = (good_set_parity + parities[self.good_index]) % 2 # choose from x0+b0, x1+b1 or x0+b1, x1+b0 the one that contains the good set
        return retrieved_bit
        

    def execute(self, sender="Alice"):
        with CQCConnection(self.name) as self.cqc:
            self.receive_qubits(sender)
            print("receiving basis")
            basis_list = self.receive_basis_information(sender)
            sets = self.perform_basis_sift(basis_list)
            print("sending sets")
            self.send_sets(sender, sets)
            print("receiving parities")
            good_set_parity = self.receive_parities_addresses(sets, sender)
            print("sending choice")
            bit = self.get_chosen_bit(sender, good_set_parity)
            print('Bit %s is %s' % (self.decision_bit, bit))



if __name__ == "__main__":
    recv = Receiver(1)
    recv.execute()