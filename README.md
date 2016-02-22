This is a simulation of a cellular automaton decoder for the toric code. 
While there are many nonlocal decoders for the toric code, such as the 
Bravyi-Haah decoder, this is an attempt to find out numerically whether a 
local decoder could improve the lifetime of a quantum memory. Physically, 
such a decoder could be programmed into the dynamics of an atomic lattice. 


In each round five things happen:

1. The cellular automaton measures local stabilizers of the toric code and 
changes internal state.
2. The cellular automaton applies bit flips according to its internal 
state
3. The cellular automaton updates according to a local rule.
4. i.i.d bit flip noise is applied to each qubit of the toric code.
5. The stored information of the quantum memory is checked for errors by 
hypothetically decoding using the Bravyi-Haah decoder. 

The cellular automaton is iterated over time until failure occurs.
