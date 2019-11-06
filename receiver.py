from cqc.pythonLib import CQCConnection, qubit
from communication import send_message, receive_message
from functools import partial
import random
import numpy as np
from utils import call, prepare_func

class Receiver(object):
    def __init__(self, name="Bob"):
        self.cqc = None
        self.name = name

        self.N =10

        # self.cqc = CQCConnection(self.name)

    def __del__(self):
        del self.cqc

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
        parities = []
        parities.append([int(x) for x in receive_message(self.cqc, sender)])
        parities.append([int(x) for x in receive_message(self.cqc, sender)])

        parity = 0
        for i in range(0, len(parities[self.good_index])):
            parity = (parity + sets[self.good_index][parities[self.good_index][i]]) % 2

        return parity

    def get_chosen_bit(self, sender, good_set_parity):
        send_message(self.cqc, sender, [self.good_index == self.decision_bit])
        parities = receive_message(self.cqc, sender)
        retrieved_bit = (good_set_parity + parities[self.good_index]) % 2 # choose from x0+b0, x1+b1 or x0+b1, x1+b0 the one that contains the good set
        return retrieved_bit

    def _execute_bit_ot(self, decision_bit, sender="Alice", cqc=None):        
        self.cqc = cqc
        self.raw_key = []
        self.basis_list = []
        self.sifted_basis = []

        self.decision_bit = decision_bit
        self.good_index = None

        self.receive_qubits(sender)
        # print("receiving basis")
        basis_list = self.receive_basis_information(sender)
        sets = self.perform_basis_sift(basis_list)
        # print("sending sets")
        self.send_sets(sender, sets)
        # print("receiving parities")
        good_set_parity = self.receive_parities_addresses(sets, sender)
        # print("sending choice")
        bit = self.get_chosen_bit(sender, good_set_parity)
        # print('Bit %s is %s' % (int(self.decision_bit), int(bit)))
        return bit

    def _execute_rot(self, n, sender="Alice", cqc=None): 
        self.cqc = cqc
        c = random.random() < 0.5
        rc = []
        for _ in range(0, n):
            rc.append(self.execute_bit_ot(c))
        m = []
        k = int(n/2)
        m.append(np.asarray(list(receive_message(self.cqc, sender)), dtype=np.uint8).reshape(k, n))
        m.append(np.asarray(list(receive_message(self.cqc, sender)), dtype=np.uint8).reshape(k, n))
        return c, np.matmul(m[c], np.asarray(rc, dtype=np.uint8).T).T

    def _execute_string_ot(self, c, n, sender="Alice", cqc=None):
        self.cqc = cqc
        c_prime, rc = self.execute_rot(n*2)
        
        d = (c+c_prime)%2
        send_message(self.cqc, sender, [d])
        e = []
        e.append([int(x) for x in receive_message(self.cqc, sender)])
        e.append([int(x) for x in receive_message(self.cqc, sender)])
        ac = list((np.asarray(e[c], dtype=np.uint8) + rc)%2)
        #print(ac)
        return ac

    def execute_string_ot(self, n, sender="Alice", cqc=None):
        return call(prepare_func(self._execute_string_ot, n, sender ), self.name, cqc)

    def execute_rot(self, n, sender="Alice", cqc=None):
        return call(prepare_func(self._execute_rot, n, sender), self.name, cqc)

    def execute_bit_ot(self, decision_bit, sender="Alice", cqc=None):
        return call(prepare_func(self._execute_bit_ot, decision_bit, sender), self.name, cqc)



if __name__ == "__main__":
    recv = Receiver()
    recv.execute_string_ot(0,4)
    # recv.receive_msg()