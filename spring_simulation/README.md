<h1 align="center"> Horizontal Spring-Mass Simulator </h1>

<p align="center">A 2D interactive horizontal spring-mass simulator which oscillates about x-axis back and froth purely made using <b>Python</b> and its libraries like <b>numpy</b> and <b>pygame</b>.</p>

<p align="center">
  <img src="assets/demo.gif" alt="Spring-mass simulation demo" width="700">
</p>

---

## 📖 About

This simulation lets user control **mass**, **stiffness coefficent** and **damping coefficent** in real time and lets them observer how each factor affect the oscilation of the spring, helping visual learners and teaching people how spring behaves.

🎥 [Watch the video]()

## ✨ Features:
- **Interactive**: you can interact with the system by dragging the mass
- **Adjustable mass**: mass of the system can be controlled in real time using slidebar
- **Adjustable stiffness**: you can observe how stiffness coefficent affect the spring behavior 
- **Adjustable damping**: using slidebar you can experiment with damping of the system
- **Force Visualization**: you can see which force in acting on which direction and with what magnitude
- **Live calculation**: you can observe the values changing live in the right-bottom block
- **Reset**: by pressing "R" you can restore the simulation inital state

## 📐 Physics behind simulation:
A horizontal spring-mass system is simulated using equations like,
- **Hooke's law**: spring_force =  -stiffness coefficient * displacement
- **Damping force(2D)**: damping force = -damping coefficient * velocity
- **Newton 2nd law**: net_force = mass * acceleration
- **Kinetic energy**: 0.5 * mass * velcoity^2
- **Potential energy of spring**: 0.5 * stiffness coeffcient * displacement^2

## 🚀 How to run:
```bash

```
