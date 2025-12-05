# Logic Circuit Simulator - EECE 2140 Final Project

## Project Goal

This project is an interactive logic circuit simulator built with Python and Pygame. The goal is to provide a visual, drag-and-drop interface where users can:

- Design digital logic circuits using logic gates (AND, NAND, OR, NOR, XOR, XNOR, NOT, Buffer)
- Connect gates with wires to create complex circuits
- Set input values (A, B, C) and observe output results
- **Automatically generate truth tables** for the created circuits
- Learn about digital logic in an intuitive, hands-on way

The simulator supports up to **3-input circuits** and dynamically evaluates the circuit logic to produce accurate truth tables, making it an excellent educational tool for understanding Boolean logic and digital circuit design.

---

## How to Run the Code

### Step-by-Step Instructions

1. **Clone or Download the Repository**
   ```bash
   git clone https://github.com/davidcharles7/EECE2140_Final.git
   cd EECE2140_Final/EECE2140_Final
   ```

2. **Install Python** (if not already installed)
   - Python 3.7 or higher is required
   - Download from [python.org](https://www.python.org/downloads/)

3. **Install Required Dependencies**
   ```bash
   pip install pygame
   ```
   
   Optional (if available):
   ```bash
   pip install PyGates
   ```

4. **Run the Simulator**
   ```bash
   python main.py
   ```

5. **Using the Simulator**
   - Click **"Blocks"** to open the component tray
   - Drag gates, inputs (A, B, C), and output blocks onto the canvas
   - Click **"Wire"** to enter wire mode, then click to draw wires between components
   - Click gates to select them, then use **"Info"** to view their truth tables
   - Set input values by clicking on input blocks (toggles between 0 and 1)
   - Click **"Play"** to generate the full circuit truth table
   - Use **"Reset"** to clear the circuit and start over
   - Use **"Undo"** to reverse recent actions

---

## Requirements and Dependencies

### Required
- **Python 3.7+**
- **Pygame 2.x** - Graphics and UI library
  ```bash
  pip install pygame
  ```

### Optional
- **PyGates** - External logic gate library (the code falls back to local implementations if not available)
  ```bash
  pip install PyGates
  ```

### Project Files
- `main.py` - Main game loop, UI, and event handling
- `LogicGates.py` - Logic gate class implementations (AND, OR, NOT, NAND, NOR, XOR, XNOR, Buffer)
- `logic_truth_tables.py` - Circuit evaluation and truth table generation
- `sprites.py` - Draggable sprite classes for gates and components
- `settings.py` - Configuration constants (screen size, colors, grid settings)
- `Images/` - Gate and component image assets

---

## Approach and Methodology

### 1. **Visual Circuit Design**
The simulator uses Pygame's sprite system to create draggable logic gates and components. Users interact with the circuit by:
- Dragging gates from a tray onto a grid-based canvas
- Drawing wires between gate inputs/outputs to create connections
- Setting input values (0 or 1) on input blocks

### 2. **Wire Connection System**
Wires are intelligent objects that:
- Snap to gate connection points (inputs/outputs)
- Detect connections to sprites at their endpoints
- Connect to other wires at intersection points
- Store connectivity information for circuit evaluation

### 3. **Circuit Evaluation Algorithm**
The `CircuitEvaluator` class uses a sophisticated graph-based approach:

1. **Build Connectivity Map**: Analyzes all wires to create a graph of connections between gates
2. **Two-Pass Trace Algorithm**: 
   - First pass: Resolves direct values (from inputs)
   - Second pass: Handles recursive gate dependencies
3. **Iterative Propagation**: Evaluates gates repeatedly until the circuit stabilizes
4. **Truth Table Generation**: Tests all possible input combinations (2³ = 8 rows for 3 inputs)

### 4. **Special Considerations**
- **OR/NOR Logic Swap**: The OR and NOR gate images have inverted output bubbles compared to standard notation, so their logic is swapped in code to match the visual representation
- **No Cloning**: Each gate can only be used once to simplify circuit design
- **Error Handling**: Validates circuits before evaluation (checks for required inputs/outputs, detects cycles)

---

## Results and Outputs

### Features Demonstrated

✅ **Dynamic Truth Table Generation**
- Automatically generates complete truth tables for user-created circuits
- Supports 1, 2, or 3 input circuits
- Displays results in a clean popup window with scrolling

✅ **All Logic Gates Implemented**
- AND, NAND, OR, NOR gates (2 inputs)
- XOR, XNOR gates (2 inputs)
- NOT gate (1 input)
- Buffer gate (1 input)

✅ **Interactive Wire System**
- Click-to-draw wire routing
- Wire-to-wire connections at intersections
- Visual feedback for selected wires

✅ **Input/Output System**
- Toggle input values (A, B, C) with mouse clicks
- Output block displays the final circuit result
- Live value overlays show signal propagation

✅ **User-Friendly Interface**
- Undo functionality for mistakes
- Reset button to clear the circuit
- Info button to view individual gate truth tables
- Grid-based snapping for clean circuit layouts

### Example Circuits Tested

1. **Simple AND Gate Circuit**: Input A and B → AND gate → Output
   - Truth table: 4 rows (2 inputs)
   - Verified correct AND logic

2. **3-Input Complex Circuit**: Inputs A, B, C → Multiple gates → Output
   - Truth table: 8 rows (3 inputs)
   - Successfully handles gate-to-gate connections

3. **NAND/NOR Circuits**: Tested inverse logic gates
   - All gates produce correct outputs matching their truth tables

### Screenshots

*(Note: Add screenshots of your simulator here showing:)*
- The main interface with the tray open
- A sample circuit with wires
- A generated truth table popup
- Different gate types in use

---

## Team Information

**EECE 2140 Final Project - Team 13**

Developed as a comprehensive digital logic education tool for learning Boolean algebra and circuit design principles.

---

## License

This project is created for educational purposes as part of EECE 2140 coursework.
