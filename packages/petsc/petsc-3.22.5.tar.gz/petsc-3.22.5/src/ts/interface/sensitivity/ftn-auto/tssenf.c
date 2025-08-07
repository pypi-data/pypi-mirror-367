#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* tssen.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include <petscts.h>
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputeijacobianp_ TSCOMPUTEIJACOBIANP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputeijacobianp_ tscomputeijacobianp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsgetcostintegral_ TSGETCOSTINTEGRAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsgetcostintegral_ tsgetcostintegral
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputecostintegrand_ TSCOMPUTECOSTINTEGRAND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputecostintegrand_ tscomputecostintegrand
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputedrdufunction_ TSCOMPUTEDRDUFUNCTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputedrdufunction_ tscomputedrdufunction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputedrdpfunction_ TSCOMPUTEDRDPFUNCTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputedrdpfunction_ tscomputedrdpfunction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputeihessianproductfunctionuu_ TSCOMPUTEIHESSIANPRODUCTFUNCTIONUU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputeihessianproductfunctionuu_ tscomputeihessianproductfunctionuu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputeihessianproductfunctionup_ TSCOMPUTEIHESSIANPRODUCTFUNCTIONUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputeihessianproductfunctionup_ tscomputeihessianproductfunctionup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputeihessianproductfunctionpu_ TSCOMPUTEIHESSIANPRODUCTFUNCTIONPU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputeihessianproductfunctionpu_ tscomputeihessianproductfunctionpu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputerhshessianproductfunctionuu_ TSCOMPUTERHSHESSIANPRODUCTFUNCTIONUU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputerhshessianproductfunctionuu_ tscomputerhshessianproductfunctionuu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputerhshessianproductfunctionup_ TSCOMPUTERHSHESSIANPRODUCTFUNCTIONUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputerhshessianproductfunctionup_ tscomputerhshessianproductfunctionup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputerhshessianproductfunctionpu_ TSCOMPUTERHSHESSIANPRODUCTFUNCTIONPU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputerhshessianproductfunctionpu_ tscomputerhshessianproductfunctionpu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputerhshessianproductfunctionpp_ TSCOMPUTERHSHESSIANPRODUCTFUNCTIONPP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputerhshessianproductfunctionpp_ tscomputerhshessianproductfunctionpp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssetcostgradients_ TSSETCOSTGRADIENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssetcostgradients_ tssetcostgradients
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsgetcostgradients_ TSGETCOSTGRADIENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsgetcostgradients_ tsgetcostgradients
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssetcosthessianproducts_ TSSETCOSTHESSIANPRODUCTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssetcosthessianproducts_ tssetcosthessianproducts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsgetcosthessianproducts_ TSGETCOSTHESSIANPRODUCTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsgetcosthessianproducts_ tsgetcosthessianproducts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointsetforward_ TSADJOINTSETFORWARD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointsetforward_ tsadjointsetforward
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointresetforward_ TSADJOINTRESETFORWARD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointresetforward_ tsadjointresetforward
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointsetup_ TSADJOINTSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointsetup_ tsadjointsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointreset_ TSADJOINTRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointreset_ tsadjointreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointsetsteps_ TSADJOINTSETSTEPS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointsetsteps_ tsadjointsetsteps
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointcomputedrdyfunction_ TSADJOINTCOMPUTEDRDYFUNCTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointcomputedrdyfunction_ tsadjointcomputedrdyfunction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointcomputedrdpfunction_ TSADJOINTCOMPUTEDRDPFUNCTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointcomputedrdpfunction_ tsadjointcomputedrdpfunction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointstep_ TSADJOINTSTEP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointstep_ tsadjointstep
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointsolve_ TSADJOINTSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointsolve_ tsadjointsolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadjointcostintegral_ TSADJOINTCOSTINTEGRAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadjointcostintegral_ tsadjointcostintegral
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardsetup_ TSFORWARDSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardsetup_ tsforwardsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardreset_ TSFORWARDRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardreset_ tsforwardreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardsetintegralgradients_ TSFORWARDSETINTEGRALGRADIENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardsetintegralgradients_ tsforwardsetintegralgradients
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardgetintegralgradients_ TSFORWARDGETINTEGRALGRADIENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardgetintegralgradients_ tsforwardgetintegralgradients
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardstep_ TSFORWARDSTEP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardstep_ tsforwardstep
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardsetsensitivities_ TSFORWARDSETSENSITIVITIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardsetsensitivities_ tsforwardsetsensitivities
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardgetsensitivities_ TSFORWARDGETSENSITIVITIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardgetsensitivities_ tsforwardgetsensitivities
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardcostintegral_ TSFORWARDCOSTINTEGRAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardcostintegral_ tsforwardcostintegral
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardsetinitialsensitivities_ TSFORWARDSETINITIALSENSITIVITIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardsetinitialsensitivities_ tsforwardsetinitialsensitivities
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsforwardgetstages_ TSFORWARDGETSTAGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsforwardgetstages_ tsforwardgetstages
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscreatequadraturets_ TSCREATEQUADRATURETS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscreatequadraturets_ tscreatequadraturets
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsgetquadraturets_ TSGETQUADRATURETS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsgetquadraturets_ tsgetquadraturets
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tscomputesnesjacobian_ TSCOMPUTESNESJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscomputesnesjacobian_ tscomputesnesjacobian
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tscomputeijacobianp_(TS ts,PetscReal *t,Vec U,Vec Udot,PetscReal *shift,Mat Amat,PetscBool *imex, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(Udot);
CHKFORTRANNULLOBJECT(Amat);
*ierr = TSComputeIJacobianP(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),
	(Vec)PetscToPointer((Udot) ),*shift,
	(Mat)PetscToPointer((Amat) ),*imex);
}
PETSC_EXTERN void  tsgetcostintegral_(TS ts,Vec *v, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = TSGetCostIntegral(
	(TS)PetscToPointer((ts) ),v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  tscomputecostintegrand_(TS ts,PetscReal *t,Vec U,Vec Q, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(Q);
*ierr = TSComputeCostIntegrand(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),
	(Vec)PetscToPointer((Q) ));
}
PETSC_EXTERN void  tscomputedrdufunction_(TS ts,PetscReal *t,Vec U,Vec *DRDU, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool DRDU_null = !*(void**) DRDU ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(DRDU);
*ierr = TSComputeDRDUFunction(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),DRDU);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! DRDU_null && !*(void**) DRDU) * (void **) DRDU = (void *)-2;
}
PETSC_EXTERN void  tscomputedrdpfunction_(TS ts,PetscReal *t,Vec U,Vec *DRDP, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool DRDP_null = !*(void**) DRDP ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(DRDP);
*ierr = TSComputeDRDPFunction(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),DRDP);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! DRDP_null && !*(void**) DRDP) * (void **) DRDP = (void *)-2;
}
PETSC_EXTERN void  tscomputeihessianproductfunctionuu_(TS ts,PetscReal *t,Vec U,Vec Vl[],Vec Vr,Vec VHV[], int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool Vl_null = !*(void**) Vl ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Vl);
CHKFORTRANNULLOBJECT(Vr);
PetscBool VHV_null = !*(void**) VHV ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(VHV);
*ierr = TSComputeIHessianProductFunctionUU(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),Vl,
	(Vec)PetscToPointer((Vr) ),VHV);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Vl_null && !*(void**) Vl) * (void **) Vl = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! VHV_null && !*(void**) VHV) * (void **) VHV = (void *)-2;
}
PETSC_EXTERN void  tscomputeihessianproductfunctionup_(TS ts,PetscReal *t,Vec U,Vec Vl[],Vec Vr,Vec VHV[], int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool Vl_null = !*(void**) Vl ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Vl);
CHKFORTRANNULLOBJECT(Vr);
PetscBool VHV_null = !*(void**) VHV ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(VHV);
*ierr = TSComputeIHessianProductFunctionUP(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),Vl,
	(Vec)PetscToPointer((Vr) ),VHV);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Vl_null && !*(void**) Vl) * (void **) Vl = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! VHV_null && !*(void**) VHV) * (void **) VHV = (void *)-2;
}
PETSC_EXTERN void  tscomputeihessianproductfunctionpu_(TS ts,PetscReal *t,Vec U,Vec Vl[],Vec Vr,Vec VHV[], int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool Vl_null = !*(void**) Vl ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Vl);
CHKFORTRANNULLOBJECT(Vr);
PetscBool VHV_null = !*(void**) VHV ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(VHV);
*ierr = TSComputeIHessianProductFunctionPU(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),Vl,
	(Vec)PetscToPointer((Vr) ),VHV);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Vl_null && !*(void**) Vl) * (void **) Vl = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! VHV_null && !*(void**) VHV) * (void **) VHV = (void *)-2;
}
PETSC_EXTERN void  tscomputerhshessianproductfunctionuu_(TS ts,PetscReal *t,Vec U,Vec Vl[],Vec Vr,Vec VHV[], int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool Vl_null = !*(void**) Vl ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Vl);
CHKFORTRANNULLOBJECT(Vr);
PetscBool VHV_null = !*(void**) VHV ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(VHV);
*ierr = TSComputeRHSHessianProductFunctionUU(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),Vl,
	(Vec)PetscToPointer((Vr) ),VHV);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Vl_null && !*(void**) Vl) * (void **) Vl = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! VHV_null && !*(void**) VHV) * (void **) VHV = (void *)-2;
}
PETSC_EXTERN void  tscomputerhshessianproductfunctionup_(TS ts,PetscReal *t,Vec U,Vec Vl[],Vec Vr,Vec VHV[], int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool Vl_null = !*(void**) Vl ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Vl);
CHKFORTRANNULLOBJECT(Vr);
PetscBool VHV_null = !*(void**) VHV ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(VHV);
*ierr = TSComputeRHSHessianProductFunctionUP(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),Vl,
	(Vec)PetscToPointer((Vr) ),VHV);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Vl_null && !*(void**) Vl) * (void **) Vl = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! VHV_null && !*(void**) VHV) * (void **) VHV = (void *)-2;
}
PETSC_EXTERN void  tscomputerhshessianproductfunctionpu_(TS ts,PetscReal *t,Vec U,Vec Vl[],Vec Vr,Vec VHV[], int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool Vl_null = !*(void**) Vl ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Vl);
CHKFORTRANNULLOBJECT(Vr);
PetscBool VHV_null = !*(void**) VHV ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(VHV);
*ierr = TSComputeRHSHessianProductFunctionPU(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),Vl,
	(Vec)PetscToPointer((Vr) ),VHV);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Vl_null && !*(void**) Vl) * (void **) Vl = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! VHV_null && !*(void**) VHV) * (void **) VHV = (void *)-2;
}
PETSC_EXTERN void  tscomputerhshessianproductfunctionpp_(TS ts,PetscReal *t,Vec U,Vec Vl[],Vec Vr,Vec VHV[], int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool Vl_null = !*(void**) Vl ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Vl);
CHKFORTRANNULLOBJECT(Vr);
PetscBool VHV_null = !*(void**) VHV ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(VHV);
*ierr = TSComputeRHSHessianProductFunctionPP(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),Vl,
	(Vec)PetscToPointer((Vr) ),VHV);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Vl_null && !*(void**) Vl) * (void **) Vl = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! VHV_null && !*(void**) VHV) * (void **) VHV = (void *)-2;
}
PETSC_EXTERN void  tssetcostgradients_(TS ts,PetscInt *numcost,Vec *lambda,Vec *mu, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool lambda_null = !*(void**) lambda ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lambda);
PetscBool mu_null = !*(void**) mu ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mu);
*ierr = TSSetCostGradients(
	(TS)PetscToPointer((ts) ),*numcost,lambda,mu);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lambda_null && !*(void**) lambda) * (void **) lambda = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mu_null && !*(void**) mu) * (void **) mu = (void *)-2;
}
PETSC_EXTERN void  tsgetcostgradients_(TS ts,PetscInt *numcost,Vec **lambda,Vec **mu, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(numcost);
PetscBool lambda_null = !*(void**) lambda ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lambda);
PetscBool mu_null = !*(void**) mu ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mu);
*ierr = TSGetCostGradients(
	(TS)PetscToPointer((ts) ),numcost,lambda,mu);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lambda_null && !*(void**) lambda) * (void **) lambda = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mu_null && !*(void**) mu) * (void **) mu = (void *)-2;
}
PETSC_EXTERN void  tssetcosthessianproducts_(TS ts,PetscInt *numcost,Vec *lambda2,Vec *mu2,Vec dir, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool lambda2_null = !*(void**) lambda2 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lambda2);
PetscBool mu2_null = !*(void**) mu2 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mu2);
CHKFORTRANNULLOBJECT(dir);
*ierr = TSSetCostHessianProducts(
	(TS)PetscToPointer((ts) ),*numcost,lambda2,mu2,
	(Vec)PetscToPointer((dir) ));
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lambda2_null && !*(void**) lambda2) * (void **) lambda2 = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mu2_null && !*(void**) mu2) * (void **) mu2 = (void *)-2;
}
PETSC_EXTERN void  tsgetcosthessianproducts_(TS ts,PetscInt *numcost,Vec **lambda2,Vec **mu2,Vec *dir, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(numcost);
PetscBool lambda2_null = !*(void**) lambda2 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lambda2);
PetscBool mu2_null = !*(void**) mu2 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mu2);
PetscBool dir_null = !*(void**) dir ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dir);
*ierr = TSGetCostHessianProducts(
	(TS)PetscToPointer((ts) ),numcost,lambda2,mu2,dir);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lambda2_null && !*(void**) lambda2) * (void **) lambda2 = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mu2_null && !*(void**) mu2) * (void **) mu2 = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dir_null && !*(void**) dir) * (void **) dir = (void *)-2;
}
PETSC_EXTERN void  tsadjointsetforward_(TS ts,Mat didp, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(didp);
*ierr = TSAdjointSetForward(
	(TS)PetscToPointer((ts) ),
	(Mat)PetscToPointer((didp) ));
}
PETSC_EXTERN void  tsadjointresetforward_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSAdjointResetForward(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsadjointsetup_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSAdjointSetUp(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsadjointreset_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSAdjointReset(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsadjointsetsteps_(TS ts,PetscInt *steps, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSAdjointSetSteps(
	(TS)PetscToPointer((ts) ),*steps);
}
PETSC_EXTERN void  tsadjointcomputedrdyfunction_(TS ts,PetscReal *t,Vec U,Vec *DRDU, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool DRDU_null = !*(void**) DRDU ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(DRDU);
*ierr = TSAdjointComputeDRDYFunction(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),DRDU);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! DRDU_null && !*(void**) DRDU) * (void **) DRDU = (void *)-2;
}
PETSC_EXTERN void  tsadjointcomputedrdpfunction_(TS ts,PetscReal *t,Vec U,Vec *DRDP, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(U);
PetscBool DRDP_null = !*(void**) DRDP ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(DRDP);
*ierr = TSAdjointComputeDRDPFunction(
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((U) ),DRDP);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! DRDP_null && !*(void**) DRDP) * (void **) DRDP = (void *)-2;
}
PETSC_EXTERN void  tsadjointstep_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSAdjointStep(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsadjointsolve_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSAdjointSolve(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsadjointcostintegral_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSAdjointCostIntegral(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsforwardsetup_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSForwardSetUp(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsforwardreset_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSForwardReset(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsforwardsetintegralgradients_(TS ts,PetscInt *numfwdint,Vec *vp, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool vp_null = !*(void**) vp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vp);
*ierr = TSForwardSetIntegralGradients(
	(TS)PetscToPointer((ts) ),*numfwdint,vp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vp_null && !*(void**) vp) * (void **) vp = (void *)-2;
}
PETSC_EXTERN void  tsforwardgetintegralgradients_(TS ts,PetscInt *numfwdint,Vec **vp, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(numfwdint);
PetscBool vp_null = !*(void**) vp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vp);
*ierr = TSForwardGetIntegralGradients(
	(TS)PetscToPointer((ts) ),numfwdint,vp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vp_null && !*(void**) vp) * (void **) vp = (void *)-2;
}
PETSC_EXTERN void  tsforwardstep_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSForwardStep(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsforwardsetsensitivities_(TS ts,PetscInt *nump,Mat Smat, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(Smat);
*ierr = TSForwardSetSensitivities(
	(TS)PetscToPointer((ts) ),*nump,
	(Mat)PetscToPointer((Smat) ));
}
PETSC_EXTERN void  tsforwardgetsensitivities_(TS ts,PetscInt *nump,Mat *Smat, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(nump);
PetscBool Smat_null = !*(void**) Smat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Smat);
*ierr = TSForwardGetSensitivities(
	(TS)PetscToPointer((ts) ),nump,Smat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Smat_null && !*(void**) Smat) * (void **) Smat = (void *)-2;
}
PETSC_EXTERN void  tsforwardcostintegral_(TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSForwardCostIntegral(
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tsforwardsetinitialsensitivities_(TS ts,Mat didp, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(didp);
*ierr = TSForwardSetInitialSensitivities(
	(TS)PetscToPointer((ts) ),
	(Mat)PetscToPointer((didp) ));
}
PETSC_EXTERN void  tsforwardgetstages_(TS ts,PetscInt *ns,Mat **S, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(ns);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
*ierr = TSForwardGetStages(
	(TS)PetscToPointer((ts) ),ns,S);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
}
PETSC_EXTERN void  tscreatequadraturets_(TS ts,PetscBool *fwd,TS *quadts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool quadts_null = !*(void**) quadts ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(quadts);
*ierr = TSCreateQuadratureTS(
	(TS)PetscToPointer((ts) ),*fwd,quadts);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! quadts_null && !*(void**) quadts) * (void **) quadts = (void *)-2;
}
PETSC_EXTERN void  tsgetquadraturets_(TS ts,PetscBool *fwd,TS *quadts, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool quadts_null = !*(void**) quadts ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(quadts);
*ierr = TSGetQuadratureTS(
	(TS)PetscToPointer((ts) ),fwd,quadts);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! quadts_null && !*(void**) quadts) * (void **) quadts = (void *)-2;
}
PETSC_EXTERN void  tscomputesnesjacobian_(TS ts,Vec x,Mat J,Mat Jpre, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(Jpre);
*ierr = TSComputeSNESJacobian(
	(TS)PetscToPointer((ts) ),
	(Vec)PetscToPointer((x) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((Jpre) ));
}
#if defined(__cplusplus)
}
#endif
