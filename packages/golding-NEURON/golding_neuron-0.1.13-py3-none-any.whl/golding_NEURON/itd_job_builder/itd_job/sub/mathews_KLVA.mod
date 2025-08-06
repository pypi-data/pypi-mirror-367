
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}



NEURON {
	SUFFIX mathews_KLVA	USEION k READ ek WRITE ik
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
	ek=-90 (mV) 
	celsius =35		(degC)
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
 gk=gkbar*w^4*((0.82*z+0.18))
 ik=gk*(v-ek)
}





PROCEDURE states() {	: this discretized form is more stable
	evaluate_fct(v)
	w = w + (w_inf - w)*w_exp	z = z + z_exp * (z_inf - z)
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

	w_inf = 1/(1+exp(-(v+57.3)/11.7))
	tau_w = -0.0382 + 1.29*exp(-(v+70)/8.82) + 0.876*exp(-(v+70)/61.9)
	if(tau_w>=10){
	tau_w=10}

	z_inf = 1/(1+exp((v+57.0)/5.44))
	tau_z = 41.9 - 32.2/(1+ exp(-(55.4+v)/9.85))

	w_exp = 1 - exp(-dt/tau_w)
	
	z_exp = 1 - exp(-dt/tau_z)

}



UNITSON








