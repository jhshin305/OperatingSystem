# Initialize shared variables
ticket = 0  # ticket counter, used to assign tickets
turn = 0    # current turn, determines which thread can proceed
count = 0   # shared resource to be incremented

# Function to acquire the lock
def acquire():
    global ticket, turn
    my_ticket = 1
    # my_ticket = fetch_and_increment(ticket)  # Atomically grab a ticket
    my_ticket += ticket  # Atomically grab a ticket
    ticket += 1
    while turn != my_ticket:  # Wait until it's this thread's turn
        pass

# Critical section
def critical_section():
    global count
    count += 1  # Increment the shared resource

# Function to release the lock
def release():
    global turn
    turn += 1
    # fetch_and_increment(turn)  # Atomically increment the turn to allow the next thread to proceed

# Main execution (simulating multiple iterations)
def main():
    # num_iterations = 10  # Example: Number of times to execute critical section
    # for _ in range(num_iterations):
    #     acquire()  # Acquire the lock
    #     critical_section()  # Enter critical section
    #     release()  # Release the lock
	while True:
		acquire()
		critical_section()
		release()
