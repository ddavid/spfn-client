# SPFN-client
## Purpose
This small client written using simple Python TCP Sockets is supposed to implement a small server for the interaction
between a Zenfone providing point clouds from a depth sensor and a Deep Learning application that performs
geometric fitting on unordered point clouds.
- Subscribe to Point Clouds in the `.xyz` file format through a simple TCP socket 
- Predict Geometric Primitives using SPFN
- Send Predicted Primitives through TCP socket to UE4 application
