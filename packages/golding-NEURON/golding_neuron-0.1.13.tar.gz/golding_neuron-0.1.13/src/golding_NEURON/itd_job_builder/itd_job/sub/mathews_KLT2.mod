
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}



NEURON {
	SUFFIX mathews_KLT2	USEION k READ ek WRITE ik
	RANGE gkbar 
	RANGE w_inf,z_inf
	RANGE tau_w,tau_z
	RANGE w_exp,z_exp
	RANGE ik,gk
	
}




UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
gkbar	= 0.017	(mho/cm2)  
	ek=-106		(mV) 
	celsius =22		(degC)
	dt              (ms)
	v               (mV)
	
}

STATE {
	w z
}



ASSIGNED {
gk(mho/cm2)
	ik(mA/cm2)
	w_inf
	z_inf
	tau_w
	tau_z
	w_exp
	z_exp

}




BREAKPOINT {
	SOLVE states
 gk=gkbar*w^4*z
 ik=gk*(v-ek)
}





PROCEDURE states() {	: this discretized form is more stable
	evaluate_fct(v)
	w = w + w_exp * (w_inf - w)
	z = z + z_exp * (z_inf - z)
	VERBATIM
	return 0;
	ENDVERBATIM
}



UNITSOFF
INITIAL {
evaluate_fct(v)
	w= w_inf
 z= z_inf}




PROCEDURE evaluate_fct(v(mV)) {

	w_inf = 1/(1+exp(-(v+57.34)/11.7))
	tau_w = 21.5/(6*exp((v+60)/7)+24*exp(-(v+60)/50.6))+0.35

	z_inf = 0.73/(1+exp((v+67)/6.16))+ 0.27	
	tau_z = 170/(5*exp((v+60)/10)+exp(-(v+70)/8))+10.7

	w_exp = 1 - exp(-dt/tau_w)
	
	z_exp = 1 - exp(-dt/tau_z)



}



UNITSON








