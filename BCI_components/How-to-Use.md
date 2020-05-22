# How to Use BCI

- [How to Use BCI](#how-to-use-bci)
  - [Call for help](#call-for-help)
  - [Components](#components)
  - [Start BCI system](#start-bci-system)
  - [Start testing demo](#start-testing-demo)
  - [Server component](#server-component)
  - [Backend component](#backend-component)
  - [Client component](#client-component)
    - [OFFLINE mode](#offline-mode)
    - [ONLINE mode](#online-mode)
  - [EEG component](#eeg-component)

## Call for help

Send to [Email](mailto:listenzcc@mail.bnu.edu.cn "listenzcc@mail.bnu.edu.cn") for help.

## Components

Table of components

| Name    | Description                             | File                                                   |
| ------- | --------------------------------------- | ------------------------------------------------------ |
| Server  | Main server component                   | [server.py](./server.py)                               |
| Backend | Matlab computation backend              | [local_backend](./local_backend)                       |
| Client  | UI and Game simulators, in OFFLINE mode | [client_offline.py](./client_offline.py)               |
| Client  | UI and Game simulators, in ONLINE mode  | [client_online.py](./client_online.py)                 |
| EEG     | EEG device simulator                    | [tcp_server.py](../EEG_Device_Simulator/tcp_server.py) |

## Start BCI system

Run Server component to start BCI system.

It is the **CORE** component of the BCI software.

  ```cmd
  :: Starts Server component
  cd [Directory of BCI]
  python server.py
  ```

The settings are stored in [local_profile.py](./local_profile.py).  
**Be sure setting them right before starting the server**

Following is the customized parameters.

| Vars            | Description                      | Default     |
| --------------- | -------------------------------- | ----------- |
| IP              | The IP address of the server     | 'localhost' |
| PORT            | The port of the server           | 65535       |
| IP_EEG_DEVICE   | The IP address of the EEG device | '127.0.0.1' |
| PORT_EEG_DEVICE | The port of the EEG device       | 8844        |

## Start testing demo

The testing demo is designed for verifying the BCI component is working as expected.
One should follow the order to start the testing demo,
all customized parameters should stay as default.

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

4. The dataset will be stored in [DataShop](./DataShop) in [Subject00](./DataShop/Subject00) folder,  
   the [Data](./DataShop/Subject00/Data) folder contains **Offline data**,  
   the [OnlineData](./DataShop/Subject00/OnlineData) folder contains **Online data**,  
   and the model will be stored in [Model](./DataShop/Subject00/Model) folder.

## Server component

The main TCP server of the BCI software, containing the core functions.

It receives TCP connections from UI and Game for BCI controlling,
and it operates backend matlab scripts for BCI computing.

## Backend component

We use MATLAB scripts to perform BCI computation.

- In **OFFLINE** mode,
    the backend will be recording EEG data,
    and train BCI model.

- In **ONLINE** mode,
    the backend will be recording EEG data,
    and use a BCI model to generate real-time label.

The backend component is maintained and commanded automatically by the **server component**,
no action is in need for users.

## Client component

### OFFLINE mode

Simulate a classic **OFFLINE** experiment session.

### ONLINE mode

Simulate a classic **ONLINE** experiment session.

## EEG component

Simulate a **DRY EEG DEVICE**,
which has $25 channels$, and the sampling frequency is $300 Hz$.

The component will generate *fake* EEG data as $4 seconds$ long block,
the blocks switch among *resting*, *fake* and *real* motion imaging states.
It will translate them through TCP socket as an EEG device will do.

The customized parameters can be found in a [profile file](../EEG_Device_Simulator/local_profile.py).
Even though, I will not recommend to change it manually, which may cause instability.
