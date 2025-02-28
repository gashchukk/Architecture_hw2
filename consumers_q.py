import hazelcast
import time

client = hazelcast.HazelcastClient(
    cluster_name="Hello-World",
    cluster_members=["127.0.0.1:5701"]
)

queue = client.get_queue("my-bounded-queue").blocking()

print("\n--- Started listening for values ---")
while True:
    item = queue.take()
    print(f" - Read: {item}")
    time.sleep(1)

client.shutdown()