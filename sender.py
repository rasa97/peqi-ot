from cqc.pythonLib import CQCConnection, qubit
from communication import send_message, receive_message
from utils import generate_full_rank_matrix, call, prepare_func

import random
import numpy as np

class Sender(object):
    def __init__(self, name="Alice"):
        self.cqc = None
        self.name = name

        self.N = 16

        # self.cqc = CQCConnection(self.name)

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
        return receive_message(self.cqc, receiver)[0]

    def send_final_strings(self, receiver, parities, decision):
        msgs = []
        msgs.append((parities[0] + self.transfer_bits[not decision])%2)
        msgs.append((parities[1] + self.transfer_bits[decision])%2)

        send_message(self.cqc, receiver, msgs)


    def _execute_bit_ot(self, transfer_bits, receiver="Bob", cqc=None):
        self.cqc = cqc
        self.transfer_bits = transfer_bits
        self.raw_key = []
        self.basis_list = []
    
        self.send_qubits(receiver)
        # print("sending basis")
        self.send_basis_information(receiver)
        # print("receiving sets")
        sets = self.receive_sets(receiver)
        # print("sending parities")
        parities = self.send_parities_addresses(receiver, sets)
        # print("receiving choice")
        decision = self.receive_decision(receiver)
        # print("sending final strings")
        self.send_final_strings(receiver, parities, decision)

    def _execute_rot(self, n, receiver="Bob", cqc=None):
        self.cqc = cqc
        r0 = [random.random() < 0.5 for _ in range(0, n)]
        r1 = [random.random() < 0.5 for _ in range(0, n)]
        for i in range(0, n):
            self.execute_bit_ot([r0[i], r1[i]])

        k = int(n/2)
        m0 = generate_full_rank_matrix(k,n)
        m1 = generate_full_rank_matrix(k,n)

        send_message(self.cqc, receiver, list(m0.flatten()))
        send_message(self.cqc, receiver, list(m1.flatten()))

        return np.matmul(m0, np.asarray(r0, dtype=np.uint8).T).T, np.matmul(m1, np.asarray(r1, dtype=np.uint8).T).T

    def _execute_string_ot(self, a0, a1, receiver="Bob", cqc=None):
        self.cqc = cqc
        r = self.execute_rot(len(a0)*2)
        d = receive_message(self.cqc, receiver)[0]
        e = []
        
        e.append((np.asarray(a0, dtype=np.uint8) + np.asarray(r[d], dtype=np.uint8))%2)
        e.append((np.asarray(a1, dtype=np.uint8) + np.asarray(r[(d+1)%2], dtype=np.uint8))%2)
        
        send_message(self.cqc, "Bob", e[0])
        send_message(self.cqc, "Bob", e[1])

    def execute_string_ot(self, a0, a1, receiver="Bob", cqc=None):
        return call(prepare_func(self._execute_string_ot, a0, a1, receiver), self.name)

    def execute_rot(self, n, receiver="Bob", cqc=None):
        return call(prepare_func(self._execute_rot, n, receiver), self.name)

    def execute_bit_ot(self, transfer_bits, receiver="Bob", cqc=None):
        return call(prepare_func(self._execute_bit_ot, transfer_bits, receiver), self.name)


if __name__ == "__main__":
    sender = Sender()
    sender.execute_string_ot([0]*4, [1]*4)
    # sender.send_msg()