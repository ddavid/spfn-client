# SPFN-client
## Purpose
This small client written using `asyncio` is supposed to implement a small client for the interaction between a Zenfone providing point clouds from a depth sensor and a Deep Learning application that performs geometry fitting on unordered point clouds.
- Subscribe to Point Clouds in the `.xyz` file format through a PC topic
- Publish Predictions to an according topic
