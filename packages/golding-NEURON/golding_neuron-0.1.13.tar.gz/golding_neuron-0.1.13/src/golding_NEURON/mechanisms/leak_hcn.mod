NEURON { 
	SUFFIX leak_hcn
	USEION h READ eh WRITE ih
	RANGE ih, g
}

PARAMETER {
	g = 0.001 (siemens/cm2) < 0, 1e9 >
	eh
}

ASSIGNED {
	ih (milliamp/cm2)
	v (millivolt)
}

BREAKPOINT { ih = g*(v-eh) } 

