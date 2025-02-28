import hazelcast

client = hazelcast.HazelcastClient(
    cluster_name="Hello-World",
    cluster_members=["127.0.0.1:5701"]
)

my_map = client.get_map("my-distributed-map").blocking()

for i in range(1000):
    my_map.put(i, f"value- {i}")

for key, val in my_map.entry_set():
    print(key, val)

client.shutdown()
