
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}



NEURON {
SUFFIX khurana_klva	USEION k  READ ek  WRITE ik VALENCE 1  RANGE gkbar RANGE w_inf,tau_w,z_inf,tau_z RANGE ik,gk }





UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}



PARAMETER {
gkbar= 0.012	(mho/cm2) ek= -106 (mv)

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
gk=gkbar*(w^4)*z
ik=gk*(v-ek)
}






INITIAL {
	w=(w_inf(v)/tau_w(v))*(1-w)-(1-w_inf(v))/tau_w(v)  z=(z_inf(v)/tau_z(v))*(1-z)-(1-z_inf(v))/tau_z(v)
}


DERIVATIVE states{
	w'= (w_inf(v) - w)/tau_w(v)
	z'= (z_inf(v) - z)/tau_z(v)   }

FUNCTION w_inf(Vm (mV)) (/ms) {
	UNITSOFF 
	w_inf = 1/(1+exp(-(Vm+57.3)/(11.7)))
	UNITSON
}

FUNCTION z_inf(Vm (mV)) (/ms) {
	UNITSOFF 
	z_inf =0.22 +  0.78/(1+exp((Vm+57)/(5.44)))
	UNITSON
}


FUNCTION tau_w(Vm (mV)) (/ms) {
	UNITSOFF 
	tau_w= 46/(6*exp((Vm+75)/12.15) +24*exp(-(Vm+75)/25) + 0.55 )
	UNITSON
}

FUNCTION tau_z(Vm (mV)) (/ms) {
	UNITSOFF 
	tau_z= 0.24*(1000/(exp((Vm+60)/20) + exp(-(Vm+60)/8)) +50 )
	UNITSON
}





