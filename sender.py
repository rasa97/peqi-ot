from cqc.pythonLib import CQCConnection, qubit

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
            # qubit_received = communication.receive_message(self.cqc, self.receiver_pkey)
            # print_progress_bar(i, self.N-1)

        # done_receiving = communication.receive_message(self.cqc, self.receiver_pkey)
        # assert done_receiving == 'DONE'

    
    def send_basis_information(self, receiver):
        self.cqc.sendClassical(receiver, self.basis_list)

    def receive_sets(self):
        set0 = [int(x) for x in self.cqc.recvClassical()]
        set1 = [int(x) for x in self.cqc.recvClassical()]
        return set0, set1
        
    def send_parities_addresses(self, receiver, sets):
        parities = [[], []]
        for i in range(0, len(sets)):
            for j in range(0, len(sets[i])):
                if random.randint(0,1):
                    parities[i].append(j)

        self.cqc.sendClassical(receiver, parities[0])
        self.cqc.sendClassical(receiver, parities[1])

        calculated_parities = [0, 0]
        for i in range(0, len(parities)):
            for j in range(0, len(parities[i])):
                calculated_parities[i] = (calculated_parities[i] + parities[i][j]) % 2 

        return calculated_parities

    def receive_decision(self):
        return int(self.cqc.recvClassical())

    def send_final_strings(self, receiver, parities, decision):
        msgs = []
        msgs.append((parities[0] + self.transfer_bits[decision])%2)
        msgs.append((parities[1] + self.transfer_bits[not decision])%2)

        self.cqc.sendClassical(receiver, msgs[0])
        self.cqc.sendClassical(receiver, msgs[1])


    def execute(self, receiver="Bob"):
        with CQCConnection(self.name) as self.cqc:
            self.send_qubits(receiver)
            print("sending basis")
            self.send_basis_information(receiver)
            print("receiving sets")
            sets = self.receive_sets()
            print("sending parities")
            parities = self.send_parities_addresses(receiver, sets)
            print("receiving choice")
            decision = self.receive_decision()
            print("sending final strings")
            self.send_final_strings(receiver, parities, decision)

if __name__ == "__main__":
    sender = Sender([0,1])
    sender.execute()