
import hazelcast
import time
from concurrent.futures import ThreadPoolExecutor

def reset_key():
    """Reset the key value to 0 for a clean test"""
    client = hazelcast.HazelcastClient(
    cluster_name="Hello-World",
    cluster_members=["127.0.0.1:5701","127.0.0.1:5702","127.0.0.1:5703"]
    )
    distributed_map = client.get_map("distributed-map").blocking()
    distributed_map.put("key", 0)
    client.shutdown()

def no_locks_task(client_id):
    """Increment key 10K times without using locks"""
    client = hazelcast.HazelcastClient(
    cluster_name="Hello-World",
    cluster_members=["127.0.0.1:5701","127.0.0.1:5702","127.0.0.1:5703"]
    )
    distributed_map = client.get_map("distributed-map").blocking()
    
    for _ in range(10000):
        value = distributed_map.get("key")
        value += 1
        distributed_map.put("key", value)
    
    print(f"No locks - Client {client_id} finished.")
    client.shutdown()

def pessimistic_locks_task(client_id):
    """Increment key 10K times using pessimistic locking"""
    client = hazelcast.HazelcastClient(
    cluster_name="Hello-World",
    cluster_members=["127.0.0.1:5701","127.0.0.1:5702","127.0.0.1:5703"]
    )
    distributed_map = client.get_map("distributed-map").blocking()
    
    for _ in range(10000):
        distributed_map.lock("key")
        try:
            value = distributed_map.get("key")
            value += 1
            distributed_map.put("key", value)
        finally:
            distributed_map.unlock("key")
    
    print(f"Pessimistic locks - Client {client_id} finished.")
    client.shutdown()

def optimistic_locks_task(client_id):
    """Increment key 10K times using optimistic locking"""
    client = hazelcast.HazelcastClient(
    cluster_name="Hello-World",
    cluster_members=["127.0.0.1:5701","127.0.0.1:5702","127.0.0.1:5703"]
    )
    distributed_map = client.get_map("distributed-map").blocking()
    
    for _ in range(10000):
        while True:
            old_value = distributed_map.get("key")
            new_value = old_value + 1
            
            if distributed_map.replace_if_same("key", old_value, new_value):
                break
    
    print(f"Optimistic locks - Client {client_id} finished.")
    client.shutdown()

def run_test(mode):
    """Run test with 3 clients using specified locking mode"""
    print(f"\n--- Starting {mode} test ---")
    
    reset_key()
    
    start_time = time.time()
    
    if mode == "no_locks":
        task_func = no_locks_task
    elif mode == "pessimistic_locks":
        task_func = pessimistic_locks_task
    else:
        task_func = optimistic_locks_task
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(3):
            executor.submit(task_func, i+1)
    
    execution_time = time.time() - start_time
    
    verification_client = hazelcast.HazelcastClient(
    cluster_name="Hello-World",
    cluster_members=["127.0.0.1:5701","127.0.0.1:5702","127.0.0.1:5703"]
    )
    verification_map = verification_client.get_map("distributed-map").blocking()
    final_value = verification_map.get("key")
    verification_client.shutdown()
    
    print(f"{mode} - Final value: {final_value}")
    print(f"{mode} - Expected value (30,000): {'Yes' if final_value == 30000 else 'No'}")
    print(f"{mode} - Execution time: {execution_time:.3f} seconds")
    
    return {"mode": mode, "final_value": final_value, "time": execution_time}

def main():
    results = []

    for mode in ["no_locks", "pessimistic_locks", "optimistic_locks"]:
        result = run_test(mode)
        results.append(result)
    
    print("\n--- Comparison Results ---")
    print("{:<20} {:<15} {:<15}".format("Mode", "Final Value", "Time (seconds)"))
    print("-" * 50)
    
    for result in results:
        print("{:<20} {:<15} {:<15.3f}".format(
            result["mode"], 
            result["final_value"], 
            result["time"]
        ))
    
    pessimistic_time = next(r["time"] for r in results if r["mode"] == "pessimistic_locks")
    optimistic_time = next(r["time"] for r in results if r["mode"] == "optimistic_locks")
    
    print("\n--- Analysis ---")
    if pessimistic_time < optimistic_time:
        print("Pessimistic locking was faster by {:.3f} seconds".format(optimistic_time - pessimistic_time))
    else:
        print("Optimistic locking was faster by {:.3f} seconds".format(pessimistic_time - optimistic_time))

if __name__ == "__main__":
    main()