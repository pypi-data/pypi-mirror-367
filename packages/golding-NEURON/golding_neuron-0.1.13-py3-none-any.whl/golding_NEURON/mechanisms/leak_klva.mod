NEURON { 
	SUFFIX leak_klva
	USEION k READ ek WRITE ik
	RANGE ik, g
}

PARAMETER {
	g = 0.001 (siemens/cm2) < 0, 1e9 >
	ek
}

ASSIGNED {
	ik (milliamp/cm2)
	v (millivolt)
}

BREAKPOINT { ik = g*(v-ek) } 

