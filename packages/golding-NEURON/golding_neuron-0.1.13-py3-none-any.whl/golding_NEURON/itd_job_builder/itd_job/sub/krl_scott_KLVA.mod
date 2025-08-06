
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}



NEURON {
SUFFIX krl_scott_KLVA	USEION k  READ ek  WRITE ik VALENCE 1  RANGE gkbar RANGE w_inf,tau_w,z_inf,tau_z RANGE ik,gk }





UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}



PARAMETER {
gkbar= 0.06	(mho/cm2) ek= -90 (mv)

} 


ASSIGNED {
gk(mho/cm2)
	ik(mA/cm2)
 v (mV)
}
    


STATE {
	w z }




BREAKPOINT {
SOLVE states
 METHOD cnexp 
gk=gkbar*w^4*((0.82*z+0.18))
ik=gk*(v-ek)
}






INITIAL {
	w=(w_inf(v)/tau_w(v))*(1-w)-(1-w_inf(v))/tau_w(v)  z=(z_inf(v)/tau_z(v))*(1-z)-(1-z_inf(v))/tau_z(v)
}


DERIVATIVE states{
	w'= (w_inf(v) - w)/tau_w(v)
	z'= (z_inf(v) - z)/tau_z(v) }

FUNCTION w_inf(Vm (mV)) (/ms) {
	UNITSOFF 
	w_inf = 1/(1+exp(-(Vm+57.3)/11.7))
	UNITSON
}

FUNCTION z_inf(Vm (mV)) (/ms) {
	UNITSOFF 
	z_inf =1/(1+exp((Vm+57.0)/5.44))
	UNITSON
}


FUNCTION tau_w(Vm (mV)) (/ms) {
	UNITSOFF 
	tau_w= -0.0382 + 1.29*exp(-(Vm+70)/8.82) + 0.876*exp(-(Vm+70)/61.9)
	if(tau_w>=10){
	tau_w=10}
	UNITSON
}

FUNCTION tau_z(Vm (mV)) (/ms) {
	UNITSOFF 
	tau_z= 41.9 - 32.2/(1+ exp(-(55.4+Vm)/9.85))
	UNITSON
}





