"""
instruction.py

Defines object representations necessary to track and propagate taint.
"""

# Taint Flags
# If flags change, edit function get_taint_as_string().
TAINT_LOC = 0x1
TAINT_ID = 0x10
TAINT_NAME = 0x100
TAINT_FACE = 0x1000
TAINT_PASSWORD = 0x10000
TAINT_OTHER = 0x100000


# Captures values and their taint.
class ValueTaint():
    def __init__(self, value, taint):
        self.value = value
        self.taint = taint

    def get_value(self):
        return self.value

    def get_taint(self):
        return self.taint

    def add_taint(self, taint):
        self.taint = self.taint | taint

    def remove_taint(self, taint):
        self.taint = self.taint | (~taint)

    def print_taint_as_string(taint):
        taint_string = ""
        if (taint & TAINT_LOC):
            taint_string += "|TAINT_LOC"
        if (taint & TAINT_ID):
            taint_string += "|TAINT_ID"
        if (taint & TAINT_NAME):
            taint_string += "|TAINT_NAME"
        if (taint & TAINT_FACE):
            taint_string += "|TAINT_FACE"
        if (taint & TAINT_PASSWORD):
            taint_string += "|TAINT_PASSWORD"
        if (taint & TAINT_OTHER):
            taint_string += "|TAINT_OTHER"
        return taint_string[1:]


# Defines rules for taint propagation.
class TaintPolicy():
    def __init__(self, instruction_policy, mem_size):
        # Keep track of taint stats.
        self.taint_level = 0
        self.num_tainted_instructions_run = 0
        self.time_in_taint_mode = 0

        # As opposed to check mode which is regular execution.
        self.is_taint_mode = False

        # Taint policy should be an abstraction.
        self._policy = instruction_policy

    # True iff tokens are tainted.
    def tainted_args(self, instr):
        # TODO: implement taint checking
        pass

    # Update taint state according to instruction and current policy.
    def propagate_taint(self, instr):
        self.num_tainted_instructions_run += 1
        # TODO: implement taint propagation
