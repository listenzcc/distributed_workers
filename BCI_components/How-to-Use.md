# How to Use BCI

- [How to Use BCI](#how-to-use-bci)
  - [Components](#components)
  - [Start order](#start-order)
  - [Server component](#server-component)
  - [Client component](#client-component)
    - [OFFLINE mode](#offline-mode)
    - [ONLINE mode](#online-mode)
  - [EEG component](#eeg-component)

## Components

Table of components

| Name   | Description                             | File                                                   |
| ------ | --------------------------------------- | ------------------------------------------------------ |
| Server | Main server component                   | [server.py](./server.py)                               |  |
| Client | UI and Game simulators, in OFFLINE mode | [client_offline.py](./client_offline.py)               |
| Client | UI and Game simulators, in ONLINE mode  | [client_online.py](./client_online.py)                 |
| EEG    | EEG device simulator                    | [tcp_server.py](../EEG_Device_Simulator/tcp_server.py) |

## Start order

One should follow the order to start the testing demo.

1. Run EEG simulator

    Start EEG device simulator.
    When BCI is working, it will feed simulated data to MATLAB backend.

    ```cmd
    :: Starts EEG simulator
    cd [Directory of EEG simulator]
    python tcp_server.py
    ```

2. Run Server component

    Start Server component, the **CORE** component of the BCI software.

    ```cmd
    :: Starts Server component
    cd [Directory of BCI]
    python server.py
    ```

3. Run Client component (OFFLINE or ONLINE mode)

    Start simulate a BCI experiment.

    - OFFLINE mode
        The **no feedback** mode, server will read EEG data and train a model.
        The simulation lasts about 200 seconds.

        ```cmd
        :: Starts Client component in OFFLINE mode
        cd [Directory of BCI]
        python client_offline.py
        ```

    - ONLINE mode
        The **feedback** mode, server will read EEG data and a pre-trained model, 

        ```cmd
        :: Starts Client component in ONLINE mode
        cd [Directory of BCI]
        python client_online.py
        ```

## Server component

The main TCP server of the BCI software, containing the core functions.

It receives TCP connections from UI and Game for BCI controlling,
and it operates backend matlab scripts for BCI computing.

## Client component

### OFFLINE mode

### ONLINE mode

## EEG component
