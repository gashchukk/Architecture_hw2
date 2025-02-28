import hazelcast

client = hazelcast.HazelcastClient(
    cluster_name="Hello-World",
    cluster_members=["127.0.0.1:5701"]
)
queue = client.get_queue("my-bounded-queue").blocking()

print("\n--- Started writing (1 - 100) ---")
for i in range(1, 101):
    queue.put(i)
    print(f" - Wrote: {i}")
print("\n--- Writing Finished ---")
client.shutdown()