from cqc.pythonLib import CQCConnection, qubit
from communication import send_message, receive_message

import random

class Sender(object):
    def __init__(self, transfer_bits, name="Alice"):
        self.cqc = None
        self.name = name
        self.transfer_bits = transfer_bits

        self.N = 32

        self.raw_key = []
        self.basis_list = []


    def send_qubits(self, receiver):
        
        print("Sending {} qubits...".format(self.N))
        for _ in range(0, self.N):

            # Generate a key bit
            k = random.randint(0, 1)
            self.raw_key.append(k)
            chosen_basis = random.randint(0, 1)
            self.basis_list.append(chosen_basis)

            # Create a qubit
            q = qubit(self.cqc)

            # Encode the key in the qubit
            if k == 1:
                q.X()
            # Encode in H basis if basis = 1
            if chosen_basis == 1:
                q.H()

            self.cqc.sendQubit(q, receiver)

    
    def send_basis_information(self, receiver):
        send_message(self.cqc, receiver, self.basis_list)

    def receive_sets(self, receiver):
        set0 = [int(x) for x in receive_message(self.cqc, receiver)]
        set1 = [int(x) for x in receive_message(self.cqc, receiver)]
        return set0, set1
        
    def send_parities_addresses(self, receiver, sets):
        parities = [[], []]
        for i in range(0, len(sets)):
            for j in range(0, len(sets[i])):
                if random.randint(0,1):
                    parities[i].append(j)

        send_message(self.cqc, receiver, parities[0])
        send_message(self.cqc, receiver, parities[1])

        calculated_parities = [0, 0]
        for i in range(0, len(parities)):
            for j in range(0, len(parities[i])):
                calculated_parities[i] = (calculated_parities[i] + sets[i][parities[i][j]]) % 2 

        return calculated_parities

    def receive_decision(self, receiver):
        return int.from_bytes(receive_message(self.cqc, receiver), 'little')

    def send_final_strings(self, receiver, parities, decision):
        msgs = []
        msgs.append((parities[0] + self.transfer_bits[not decision])%2)
        msgs.append((parities[1] + self.transfer_bits[decision])%2)

        send_message(self.cqc, receiver, msgs[0])
        send_message(self.cqc, receiver, msgs[1])


    def execute(self, receiver="Bob"):
        with CQCConnection(self.name) as self.cqc:
            self.send_qubits(receiver)
            print("sending basis")
            self.send_basis_information(receiver)
            print("receiving sets")
            sets = self.receive_sets(receiver)
            print("sending parities")
            parities = self.send_parities_addresses(receiver, sets)
            print("receiving choice")
            decision = self.receive_decision(receiver)
            print("sending final strings")
            self.send_final_strings(receiver, parities, decision)

if __name__ == "__main__":
    sender = Sender([0,1])
    sender.execute()