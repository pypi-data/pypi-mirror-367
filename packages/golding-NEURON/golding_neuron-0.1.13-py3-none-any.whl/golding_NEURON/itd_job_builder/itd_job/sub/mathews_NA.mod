
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}



NEURON {
	SUFFIX mathews_NA	USEION na READ ena WRITE ina	RANGE gnabar 
	RANGE m_inf,h_inf
	RANGE tau_m,tau_h	RANGE m_exp,h_exp
	RANGE ina,gna
	
}




UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
gnabar	= 0.03	(mho/cm2)  
	ena=55 (mV) 
	celsius =35		(degC)
	dt              (ms)
	v               (mV)
	
}     

STATE {
	m h}



ASSIGNED {
gna(mho/cm2)
	ina(mA/cm2)
	h_inf
	m_inf
	tau_m	tau_h	m_exp
	h_exp

}




BREAKPOINT {
	SOLVE states
 gna=gnabar*m^4*((0.993*h)+0.007)
 ina=gna*(v-ena)
}





PROCEDURE states() {	: this discretized form is more stable
	evaluate_fct(v)
	m = m+ (m_inf - m)*m_exp	h = h + h_exp * (h_inf - h)
	VERBATIM
	return 0;
	ENDVERBATIM
}



UNITSOFF
INITIAL {
evaluate_fct(v)
	h= h_inf
 m= m_inf}




PROCEDURE evaluate_fct(v(mV)) {

	m_inf = 1/(1+exp((v+46)/(-11)))
	tau_m = (0.141 + (-0.0826)/(1+exp((-20.5-v)/10.8)))/3

	h_inf = 1/(1+exp((v+62.5)/(7.77)))
	tau_h = (4 + (-3.74)/(1+exp((-40.6-v)/5.05)))/3

	m_exp = 1 - exp(-dt/tau_m)
	
	h_exp = 1 - exp(-dt/tau_h)

}



UNITSON








