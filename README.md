# Architecture_hw2
Author: Bohdan Hashchuk

```
docker run -d --name hazelcast1 -p 5701:5701 hazelcast/hazelcast:latest
docker run -d --name hazelcast2 -p 5702:5701 hazelcast/hazelcast:latest
docker run -d --name hazelcast3 -p 5703:5701 hazelcast/hazelcast:latest
```
## Management Center
```
docker run -d --name hazelcast-mc -p 8080:8080 hazelcast/management-center:latest
```