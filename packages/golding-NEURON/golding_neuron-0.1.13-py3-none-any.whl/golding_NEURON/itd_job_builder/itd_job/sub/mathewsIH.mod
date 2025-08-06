
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}



NEURON {
SUFFIX mathewsIH	USEION k  READ ek  WRITE ik	  RANGE gkbar,ik,gk


 }





UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}



PARAMETER {
gkbar= 0.03	(mho/cm2) 

} 


ASSIGNED {
gk(mho/cm2)
	ik(mA/cm2)
 v (mV) ek(mV)
}
    


STATE {
	r }




BREAKPOINT {
SOLVE states
 METHOD cnexp 
gk=gkbar*r
 
ik=gk*(v-ek)
}





INITIAL {
	r=r_ratio(v)*((r_inf(v) - r)/r_tau1(v))
 + (1-r_ratio(v))*((r_inf(v)-r)/r_tau2(v)) 
}

DERIVATIVE states{
	r'= r_ratio(v)*((r_inf(v) - r)/r_tau1(v))
 + (1-r_ratio(v))*((r_inf(v)-r)/r_tau2(v)) }

FUNCTION r_inf(Vm (mV)) (/ms) {
	UNITSOFF 
	r_inf = 1/(1+exp((Vm+64.2)/(7.32)))
	UNITSON
}


FUNCTION r_tau1(Vm (mV)) (/ms) {
	UNITSOFF 
	r_tau1= 2000 +(-1990)*exp(-(log(Vm/-128)/3.05)^2)
	if(r_tau1 >= 200){
		r_tau1 = 200}
	UNITSON
}

FUNCTION r_tau2(Vm (mV)) (/ms) {
	UNITSOFF 
	r_tau2= 8590 +(-8630)*exp(-(log(Vm/-187)/3.66)^2)
	if(r_tau2 >= 1000){
		r_tau2 = 1000}
	UNITSON
}

FUNCTION r_ratio(Vm (mV)) (/ms) {
	UNITSOFF 
	r_ratio = 0.741 + (-0.433)/(1-exp((-68.4-Vm)/9))
	UNITSON
}








