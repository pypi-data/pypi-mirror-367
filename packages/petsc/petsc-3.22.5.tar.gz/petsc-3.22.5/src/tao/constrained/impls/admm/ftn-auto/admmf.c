#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* admm.c */
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

#include "petsctao.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmsetmisfithessianchangestatus_ TAOADMMSETMISFITHESSIANCHANGESTATUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmsetmisfithessianchangestatus_ taoadmmsetmisfithessianchangestatus
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmsetreghessianchangestatus_ TAOADMMSETREGHESSIANCHANGESTATUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmsetreghessianchangestatus_ taoadmmsetreghessianchangestatus
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmsetspectralpenalty_ TAOADMMSETSPECTRALPENALTY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmsetspectralpenalty_ taoadmmsetspectralpenalty
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmgetspectralpenalty_ TAOADMMGETSPECTRALPENALTY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmgetspectralpenalty_ taoadmmgetspectralpenalty
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmgetmisfitsubsolver_ TAOADMMGETMISFITSUBSOLVER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmgetmisfitsubsolver_ taoadmmgetmisfitsubsolver
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmgetregularizationsubsolver_ TAOADMMGETREGULARIZATIONSUBSOLVER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmgetregularizationsubsolver_ taoadmmgetregularizationsubsolver
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmsetconstraintvectorrhs_ TAOADMMSETCONSTRAINTVECTORRHS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmsetconstraintvectorrhs_ taoadmmsetconstraintvectorrhs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmsetminimumspectralpenalty_ TAOADMMSETMINIMUMSPECTRALPENALTY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmsetminimumspectralpenalty_ taoadmmsetminimumspectralpenalty
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmsetregularizercoefficient_ TAOADMMSETREGULARIZERCOEFFICIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmsetregularizercoefficient_ taoadmmsetregularizercoefficient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmgetregularizercoefficient_ TAOADMMGETREGULARIZERCOEFFICIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmgetregularizercoefficient_ taoadmmgetregularizercoefficient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetadmmparenttao_ TAOGETADMMPARENTTAO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetadmmparenttao_ taogetadmmparenttao
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmgetdualvector_ TAOADMMGETDUALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmgetdualvector_ taoadmmgetdualvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmsetregularizertype_ TAOADMMSETREGULARIZERTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmsetregularizertype_ taoadmmsetregularizertype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmgetregularizertype_ TAOADMMGETREGULARIZERTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmgetregularizertype_ taoadmmgetregularizertype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmsetupdatetype_ TAOADMMSETUPDATETYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmsetupdatetype_ taoadmmsetupdatetype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoadmmgetupdatetype_ TAOADMMGETUPDATETYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoadmmgetupdatetype_ taoadmmgetupdatetype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  taoadmmsetmisfithessianchangestatus_(Tao tao,PetscBool *b, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMSetMisfitHessianChangeStatus(
	(Tao)PetscToPointer((tao) ),*b);
}
PETSC_EXTERN void  taoadmmsetreghessianchangestatus_(Tao tao,PetscBool *b, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMSetRegHessianChangeStatus(
	(Tao)PetscToPointer((tao) ),*b);
}
PETSC_EXTERN void  taoadmmsetspectralpenalty_(Tao tao,PetscReal *mu, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMSetSpectralPenalty(
	(Tao)PetscToPointer((tao) ),*mu);
}
PETSC_EXTERN void  taoadmmgetspectralpenalty_(Tao tao,PetscReal *mu, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(mu);
*ierr = TaoADMMGetSpectralPenalty(
	(Tao)PetscToPointer((tao) ),mu);
}
PETSC_EXTERN void  taoadmmgetmisfitsubsolver_(Tao tao,Tao *misfit, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool misfit_null = !*(void**) misfit ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(misfit);
*ierr = TaoADMMGetMisfitSubsolver(
	(Tao)PetscToPointer((tao) ),misfit);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! misfit_null && !*(void**) misfit) * (void **) misfit = (void *)-2;
}
PETSC_EXTERN void  taoadmmgetregularizationsubsolver_(Tao tao,Tao *reg, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool reg_null = !*(void**) reg ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(reg);
*ierr = TaoADMMGetRegularizationSubsolver(
	(Tao)PetscToPointer((tao) ),reg);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! reg_null && !*(void**) reg) * (void **) reg = (void *)-2;
}
PETSC_EXTERN void  taoadmmsetconstraintvectorrhs_(Tao tao,Vec c, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(c);
*ierr = TaoADMMSetConstraintVectorRHS(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((c) ));
}
PETSC_EXTERN void  taoadmmsetminimumspectralpenalty_(Tao tao,PetscReal *mu, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMSetMinimumSpectralPenalty(
	(Tao)PetscToPointer((tao) ),*mu);
}
PETSC_EXTERN void  taoadmmsetregularizercoefficient_(Tao tao,PetscReal *lambda, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMSetRegularizerCoefficient(
	(Tao)PetscToPointer((tao) ),*lambda);
}
PETSC_EXTERN void  taoadmmgetregularizercoefficient_(Tao tao,PetscReal *lambda, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(lambda);
*ierr = TaoADMMGetRegularizerCoefficient(
	(Tao)PetscToPointer((tao) ),lambda);
}
PETSC_EXTERN void  taogetadmmparenttao_(Tao tao,Tao *admm_tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool admm_tao_null = !*(void**) admm_tao ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(admm_tao);
*ierr = TaoGetADMMParentTao(
	(Tao)PetscToPointer((tao) ),admm_tao);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! admm_tao_null && !*(void**) admm_tao) * (void **) admm_tao = (void *)-2;
}
PETSC_EXTERN void  taoadmmgetdualvector_(Tao tao,Vec *Y, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool Y_null = !*(void**) Y ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Y);
*ierr = TaoADMMGetDualVector(
	(Tao)PetscToPointer((tao) ),Y);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Y_null && !*(void**) Y) * (void **) Y = (void *)-2;
}
PETSC_EXTERN void  taoadmmsetregularizertype_(Tao tao,TaoADMMRegularizerType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMSetRegularizerType(
	(Tao)PetscToPointer((tao) ),*type);
}
PETSC_EXTERN void  taoadmmgetregularizertype_(Tao tao,TaoADMMRegularizerType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMGetRegularizerType(
	(Tao)PetscToPointer((tao) ),type);
}
PETSC_EXTERN void  taoadmmsetupdatetype_(Tao tao,TaoADMMUpdateType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMSetUpdateType(
	(Tao)PetscToPointer((tao) ),*type);
}
PETSC_EXTERN void  taoadmmgetupdatetype_(Tao tao,TaoADMMUpdateType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoADMMGetUpdateType(
	(Tao)PetscToPointer((tao) ),type);
}
#if defined(__cplusplus)
}
#endif
