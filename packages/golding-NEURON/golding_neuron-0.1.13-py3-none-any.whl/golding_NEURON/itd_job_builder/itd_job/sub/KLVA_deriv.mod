
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}



NEURON {
	SUFFIX KLVA_deriv USEION k READ ek WRITE ik
	RANGE gkbar 
	RANGE ik,gk
	
}




UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
	gkbar = 0.017	(mho/cm2)  
	ek = -90 		(mV) 
	celsius			(degC)
	v               (mV)
	
}

ASSIGNED {
	gk(mho/cm2)
	ik(mA/cm2)

}

STATE {
	m h
}

BREAKPOINT {
	SOLVE states
	METHOD cnexp
 	gk=gkbar*m^4*h
 	ik=gk*(v-ek)
}




INITIAL {
	m = minf(v)/mtau(v)
 	h = hinf(v)/htau(v)
 }

DERIVATIVE states {

	m' = (minf(v)-m)/mtau(v)

	h' = (hinf(v)-m)/htau(v)

}

FUNCTION minf(Vm (mV)) (/ms) {

	UNITSOFF
	minf = 1/(1+exp((v+57.34)/-11.7))
	UNITSON

}

FUNCTION hinf(Vm (mV)) (/ms) {
	UNITSOFF
	hinf = (0.73/(1+exp((v+67)/6.16)))+0.27
	UNITSON

}

FUNCTION mtau(Vm (mV)) (/ms) {
	UNITSOFF
	mtau = ((6*exp((v+60)/7))+(24*exp(-((v+60)/50.6))))+0.35
	UNITSON

}

FUNCTION htau(Vm (mV)) (/ms) {
	UNITSOFF
	htau = (170/((5*exp((v+60)/10))+(exp(-((v+70)/8)))))+10.7
	UNITSON

}
COMMENT
(((1/(1+exp((v+57.34)/-11.7)))-w)/(21.5/(((6*exp((v+60)/7))+(24*exp(-((v+60)/50.6)))))+0.35))


(((0.73/(1+exp((v+67)/6.16)))-z)/(170/((5*exp((v+60)/10))+(exp(-((v+70)/8)))))+10.7
ENDCOMMENT