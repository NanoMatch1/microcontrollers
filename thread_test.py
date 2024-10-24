import threading
import queue
import time

# Create a queue to communicate between threads
q = queue.Queue()

# Producer thread function
def producer():
    for i in range(5):
        item = f"Item {i}"
        print(f"Producing {item}")
        q.put(item)  # Put the item in the queue
        time.sleep(1)  # Simulate time taken to produce an item

# Consumer thread function
def consumer():
    while True:
        item = q.get()  # Get an item from the queue
        if item is None:  # None is a signal to stop
            break
        print(f"Consuming {item}")
        time.sleep(2)  # Simulate time taken to process the item
        q.task_done()  # Mark the item as processed

# Start the producer and consumer threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

# Wait for the producer to finish
producer_thread.join()

# Add None to the queue to signal the consumer to stop
q.put(None)

# Wait for the consumer to finish
consumer_thread.join()

print("All tasks completed.")
