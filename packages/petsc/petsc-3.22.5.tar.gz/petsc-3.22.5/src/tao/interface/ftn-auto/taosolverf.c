#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* taosolver.c */
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
#define taoparametersinitialize_ TAOPARAMETERSINITIALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoparametersinitialize_ taoparametersinitialize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocreate_ TAOCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocreate_ taocreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosolve_ TAOSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosolve_ taosolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetup_ TAOSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetup_ taosetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taodestroy_ TAODESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taodestroy_ taodestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taokspsetuseew_ TAOKSPSETUSEEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taokspsetuseew_ taokspsetuseew
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetfromoptions_ TAOSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetfromoptions_ taosetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoviewfromoptions_ TAOVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoviewfromoptions_ taoviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoview_ TAOVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoview_ taoview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetrecyclehistory_ TAOSETRECYCLEHISTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetrecyclehistory_ taosetrecyclehistory
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetrecyclehistory_ TAOGETRECYCLEHISTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetrecyclehistory_ taogetrecyclehistory
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosettolerances_ TAOSETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosettolerances_ taosettolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetconstrainttolerances_ TAOSETCONSTRAINTTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetconstrainttolerances_ taosetconstrainttolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetconstrainttolerances_ TAOGETCONSTRAINTTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetconstrainttolerances_ taogetconstrainttolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetfunctionlowerbound_ TAOSETFUNCTIONLOWERBOUND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetfunctionlowerbound_ taosetfunctionlowerbound
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetfunctionlowerbound_ TAOGETFUNCTIONLOWERBOUND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetfunctionlowerbound_ taogetfunctionlowerbound
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetmaximumfunctionevaluations_ TAOSETMAXIMUMFUNCTIONEVALUATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetmaximumfunctionevaluations_ taosetmaximumfunctionevaluations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetmaximumfunctionevaluations_ TAOGETMAXIMUMFUNCTIONEVALUATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetmaximumfunctionevaluations_ taogetmaximumfunctionevaluations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetcurrentfunctionevaluations_ TAOGETCURRENTFUNCTIONEVALUATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetcurrentfunctionevaluations_ taogetcurrentfunctionevaluations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetmaximumiterations_ TAOSETMAXIMUMITERATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetmaximumiterations_ taosetmaximumiterations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetmaximumiterations_ TAOGETMAXIMUMITERATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetmaximumiterations_ taogetmaximumiterations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetinitialtrustregionradius_ TAOSETINITIALTRUSTREGIONRADIUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetinitialtrustregionradius_ taosetinitialtrustregionradius
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetinitialtrustregionradius_ TAOGETINITIALTRUSTREGIONRADIUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetinitialtrustregionradius_ taogetinitialtrustregionradius
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetcurrenttrustregionradius_ TAOGETCURRENTTRUSTREGIONRADIUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetcurrenttrustregionradius_ taogetcurrenttrustregionradius
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogettolerances_ TAOGETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogettolerances_ taogettolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetksp_ TAOGETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetksp_ taogetksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetlinearsolveiterations_ TAOGETLINEARSOLVEITERATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetlinearsolveiterations_ taogetlinearsolveiterations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetlinesearch_ TAOGETLINESEARCH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetlinesearch_ taogetlinesearch
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoaddlinesearchcounts_ TAOADDLINESEARCHCOUNTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoaddlinesearchcounts_ taoaddlinesearchcounts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetsolution_ TAOGETSOLUTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetsolution_ taogetsolution
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoresetstatistics_ TAORESETSTATISTICS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoresetstatistics_ taoresetstatistics
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taomonitorcancel_ TAOMONITORCANCEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taomonitorcancel_ taomonitorcancel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taomonitordefault_ TAOMONITORDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taomonitordefault_ taomonitordefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taomonitorglobalization_ TAOMONITORGLOBALIZATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taomonitorglobalization_ taomonitorglobalization
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taomonitordefaultshort_ TAOMONITORDEFAULTSHORT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taomonitordefaultshort_ taomonitordefaultshort
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taomonitorconstraintnorm_ TAOMONITORCONSTRAINTNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taomonitorconstraintnorm_ taomonitorconstraintnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taodefaultconvergencetest_ TAODEFAULTCONVERGENCETEST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taodefaultconvergencetest_ taodefaultconvergencetest
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetoptionsprefix_ TAOSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetoptionsprefix_ taosetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoappendoptionsprefix_ TAOAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoappendoptionsprefix_ taoappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetoptionsprefix_ TAOGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetoptionsprefix_ taogetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosettype_ TAOSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosettype_ taosettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetiterationnumber_ TAOGETITERATIONNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetiterationnumber_ taogetiterationnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetresidualnorm_ TAOGETRESIDUALNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetresidualnorm_ taogetresidualnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetiterationnumber_ TAOSETITERATIONNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetiterationnumber_ taosetiterationnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogettotaliterationnumber_ TAOGETTOTALITERATIONNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogettotaliterationnumber_ taogettotaliterationnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosettotaliterationnumber_ TAOSETTOTALITERATIONNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosettotaliterationnumber_ taosettotaliterationnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetconvergedreason_ TAOSETCONVERGEDREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetconvergedreason_ taosetconvergedreason
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetconvergedreason_ TAOGETCONVERGEDREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetconvergedreason_ taogetconvergedreason
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetsolutionstatus_ TAOGETSOLUTIONSTATUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetsolutionstatus_ taogetsolutionstatus
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogettype_ TAOGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogettype_ taogettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetconvergencehistory_ TAOSETCONVERGENCEHISTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetconvergencehistory_ taosetconvergencehistory
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetapplicationcontext_ TAOSETAPPLICATIONCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetapplicationcontext_ taosetapplicationcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetapplicationcontext_ TAOGETAPPLICATIONCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetapplicationcontext_ taogetapplicationcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetgradientnorm_ TAOSETGRADIENTNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetgradientnorm_ taosetgradientnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetgradientnorm_ TAOGETGRADIENTNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetgradientnorm_ taogetgradientnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogradientnorm_ TAOGRADIENTNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogradientnorm_ taogradientnorm
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  taoparametersinitialize_(Tao tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoParametersInitialize(
	(Tao)PetscToPointer((tao) ));
}
PETSC_EXTERN void  taocreate_(MPI_Fint * comm,Tao *newtao, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(newtao);
 PetscBool newtao_null = !*(void**) newtao ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newtao);
*ierr = TaoCreate(
	MPI_Comm_f2c(*(comm)),newtao);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newtao_null && !*(void**) newtao) * (void **) newtao = (void *)-2;
}
PETSC_EXTERN void  taosolve_(Tao tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSolve(
	(Tao)PetscToPointer((tao) ));
}
PETSC_EXTERN void  taosetup_(Tao tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetUp(
	(Tao)PetscToPointer((tao) ));
}
PETSC_EXTERN void  taodestroy_(Tao *tao, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(tao);
 PetscBool tao_null = !*(void**) tao ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoDestroy(tao);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tao_null && !*(void**) tao) * (void **) tao = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(tao);
 }
PETSC_EXTERN void  taokspsetuseew_(Tao tao,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoKSPSetUseEW(
	(Tao)PetscToPointer((tao) ),*flag);
}
PETSC_EXTERN void  taosetfromoptions_(Tao tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetFromOptions(
	(Tao)PetscToPointer((tao) ));
}
PETSC_EXTERN void  taoviewfromoptions_(Tao A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = TaoViewFromOptions(
	(Tao)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  taoview_(Tao tao,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(viewer);
*ierr = TaoView(
	(Tao)PetscToPointer((tao) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  taosetrecyclehistory_(Tao tao,PetscBool *recycle, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetRecycleHistory(
	(Tao)PetscToPointer((tao) ),*recycle);
}
PETSC_EXTERN void  taogetrecyclehistory_(Tao tao,PetscBool *recycle, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoGetRecycleHistory(
	(Tao)PetscToPointer((tao) ),recycle);
}
PETSC_EXTERN void  taosettolerances_(Tao tao,PetscReal *gatol,PetscReal *grtol,PetscReal *gttol, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetTolerances(
	(Tao)PetscToPointer((tao) ),*gatol,*grtol,*gttol);
}
PETSC_EXTERN void  taosetconstrainttolerances_(Tao tao,PetscReal *catol,PetscReal *crtol, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetConstraintTolerances(
	(Tao)PetscToPointer((tao) ),*catol,*crtol);
}
PETSC_EXTERN void  taogetconstrainttolerances_(Tao tao,PetscReal *catol,PetscReal *crtol, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(catol);
CHKFORTRANNULLREAL(crtol);
*ierr = TaoGetConstraintTolerances(
	(Tao)PetscToPointer((tao) ),catol,crtol);
}
PETSC_EXTERN void  taosetfunctionlowerbound_(Tao tao,PetscReal *fmin, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetFunctionLowerBound(
	(Tao)PetscToPointer((tao) ),*fmin);
}
PETSC_EXTERN void  taogetfunctionlowerbound_(Tao tao,PetscReal *fmin, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(fmin);
*ierr = TaoGetFunctionLowerBound(
	(Tao)PetscToPointer((tao) ),fmin);
}
PETSC_EXTERN void  taosetmaximumfunctionevaluations_(Tao tao,PetscInt *nfcn, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetMaximumFunctionEvaluations(
	(Tao)PetscToPointer((tao) ),*nfcn);
}
PETSC_EXTERN void  taogetmaximumfunctionevaluations_(Tao tao,PetscInt *nfcn, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLINTEGER(nfcn);
*ierr = TaoGetMaximumFunctionEvaluations(
	(Tao)PetscToPointer((tao) ),nfcn);
}
PETSC_EXTERN void  taogetcurrentfunctionevaluations_(Tao tao,PetscInt *nfuncs, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLINTEGER(nfuncs);
*ierr = TaoGetCurrentFunctionEvaluations(
	(Tao)PetscToPointer((tao) ),nfuncs);
}
PETSC_EXTERN void  taosetmaximumiterations_(Tao tao,PetscInt *maxits, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetMaximumIterations(
	(Tao)PetscToPointer((tao) ),*maxits);
}
PETSC_EXTERN void  taogetmaximumiterations_(Tao tao,PetscInt *maxits, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLINTEGER(maxits);
*ierr = TaoGetMaximumIterations(
	(Tao)PetscToPointer((tao) ),maxits);
}
PETSC_EXTERN void  taosetinitialtrustregionradius_(Tao tao,PetscReal *radius, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetInitialTrustRegionRadius(
	(Tao)PetscToPointer((tao) ),*radius);
}
PETSC_EXTERN void  taogetinitialtrustregionradius_(Tao tao,PetscReal *radius, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(radius);
*ierr = TaoGetInitialTrustRegionRadius(
	(Tao)PetscToPointer((tao) ),radius);
}
PETSC_EXTERN void  taogetcurrenttrustregionradius_(Tao tao,PetscReal *radius, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(radius);
*ierr = TaoGetCurrentTrustRegionRadius(
	(Tao)PetscToPointer((tao) ),radius);
}
PETSC_EXTERN void  taogettolerances_(Tao tao,PetscReal *gatol,PetscReal *grtol,PetscReal *gttol, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(gatol);
CHKFORTRANNULLREAL(grtol);
CHKFORTRANNULLREAL(gttol);
*ierr = TaoGetTolerances(
	(Tao)PetscToPointer((tao) ),gatol,grtol,gttol);
}
PETSC_EXTERN void  taogetksp_(Tao tao,KSP *ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool ksp_null = !*(void**) ksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ksp);
*ierr = TaoGetKSP(
	(Tao)PetscToPointer((tao) ),ksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ksp_null && !*(void**) ksp) * (void **) ksp = (void *)-2;
}
PETSC_EXTERN void  taogetlinearsolveiterations_(Tao tao,PetscInt *lits, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLINTEGER(lits);
*ierr = TaoGetLinearSolveIterations(
	(Tao)PetscToPointer((tao) ),lits);
}
PETSC_EXTERN void  taogetlinesearch_(Tao tao,TaoLineSearch *ls, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool ls_null = !*(void**) ls ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoGetLineSearch(
	(Tao)PetscToPointer((tao) ),ls);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ls_null && !*(void**) ls) * (void **) ls = (void *)-2;
}
PETSC_EXTERN void  taoaddlinesearchcounts_(Tao tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoAddLineSearchCounts(
	(Tao)PetscToPointer((tao) ));
}
PETSC_EXTERN void  taogetsolution_(Tao tao,Vec *X, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool X_null = !*(void**) X ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(X);
*ierr = TaoGetSolution(
	(Tao)PetscToPointer((tao) ),X);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! X_null && !*(void**) X) * (void **) X = (void *)-2;
}
PETSC_EXTERN void  taoresetstatistics_(Tao tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoResetStatistics(
	(Tao)PetscToPointer((tao) ));
}
PETSC_EXTERN void  taomonitorcancel_(Tao tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoMonitorCancel(
	(Tao)PetscToPointer((tao) ));
}
PETSC_EXTERN void  taomonitordefault_(Tao tao,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoMonitorDefault(
	(Tao)PetscToPointer((tao) ),ctx);
}
PETSC_EXTERN void  taomonitorglobalization_(Tao tao,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoMonitorGlobalization(
	(Tao)PetscToPointer((tao) ),ctx);
}
PETSC_EXTERN void  taomonitordefaultshort_(Tao tao,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoMonitorDefaultShort(
	(Tao)PetscToPointer((tao) ),ctx);
}
PETSC_EXTERN void  taomonitorconstraintnorm_(Tao tao,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoMonitorConstraintNorm(
	(Tao)PetscToPointer((tao) ),ctx);
}
PETSC_EXTERN void  taodefaultconvergencetest_(Tao tao,void*dummy, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoDefaultConvergenceTest(
	(Tao)PetscToPointer((tao) ),dummy);
}
PETSC_EXTERN void  taosetoptionsprefix_(Tao tao, char p[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tao);
/* insert Fortran-to-C conversion for p */
  FIXCHAR(p,cl0,_cltmp0);
*ierr = TaoSetOptionsPrefix(
	(Tao)PetscToPointer((tao) ),_cltmp0);
  FREECHAR(p,_cltmp0);
}
PETSC_EXTERN void  taoappendoptionsprefix_(Tao tao, char p[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tao);
/* insert Fortran-to-C conversion for p */
  FIXCHAR(p,cl0,_cltmp0);
*ierr = TaoAppendOptionsPrefix(
	(Tao)PetscToPointer((tao) ),_cltmp0);
  FREECHAR(p,_cltmp0);
}
PETSC_EXTERN void  taogetoptionsprefix_(Tao tao, char *p, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoGetOptionsPrefix(
	(Tao)PetscToPointer((tao) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for p */
*ierr = PetscStrncpy(p, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, p, cl0);
}
PETSC_EXTERN void  taosettype_(Tao tao,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tao);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = TaoSetType(
	(Tao)PetscToPointer((tao) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  taogetiterationnumber_(Tao tao,PetscInt *iter, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLINTEGER(iter);
*ierr = TaoGetIterationNumber(
	(Tao)PetscToPointer((tao) ),iter);
}
PETSC_EXTERN void  taogetresidualnorm_(Tao tao,PetscReal *value, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(value);
*ierr = TaoGetResidualNorm(
	(Tao)PetscToPointer((tao) ),value);
}
PETSC_EXTERN void  taosetiterationnumber_(Tao tao,PetscInt *iter, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetIterationNumber(
	(Tao)PetscToPointer((tao) ),*iter);
}
PETSC_EXTERN void  taogettotaliterationnumber_(Tao tao,PetscInt *iter, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLINTEGER(iter);
*ierr = TaoGetTotalIterationNumber(
	(Tao)PetscToPointer((tao) ),iter);
}
PETSC_EXTERN void  taosettotaliterationnumber_(Tao tao,PetscInt *iter, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetTotalIterationNumber(
	(Tao)PetscToPointer((tao) ),*iter);
}
PETSC_EXTERN void  taosetconvergedreason_(Tao tao,TaoConvergedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetConvergedReason(
	(Tao)PetscToPointer((tao) ),*reason);
}
PETSC_EXTERN void  taogetconvergedreason_(Tao tao,TaoConvergedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoGetConvergedReason(
	(Tao)PetscToPointer((tao) ),reason);
}
PETSC_EXTERN void  taogetsolutionstatus_(Tao tao,PetscInt *its,PetscReal *f,PetscReal *gnorm,PetscReal *cnorm,PetscReal *xdiff,TaoConvergedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLINTEGER(its);
CHKFORTRANNULLREAL(f);
CHKFORTRANNULLREAL(gnorm);
CHKFORTRANNULLREAL(cnorm);
CHKFORTRANNULLREAL(xdiff);
*ierr = TaoGetSolutionStatus(
	(Tao)PetscToPointer((tao) ),its,f,gnorm,cnorm,xdiff,reason);
}
PETSC_EXTERN void  taogettype_(Tao tao,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoGetType(
	(Tao)PetscToPointer((tao) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  taosetconvergencehistory_(Tao tao,PetscReal obj[],PetscReal resid[],PetscReal cnorm[],PetscInt lits[],PetscInt *na,PetscBool *reset, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLREAL(obj);
CHKFORTRANNULLREAL(resid);
CHKFORTRANNULLREAL(cnorm);
CHKFORTRANNULLINTEGER(lits);
*ierr = TaoSetConvergenceHistory(
	(Tao)PetscToPointer((tao) ),obj,resid,cnorm,lits,*na,*reset);
}
PETSC_EXTERN void  taosetapplicationcontext_(Tao tao,void*usrP, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoSetApplicationContext(
	(Tao)PetscToPointer((tao) ),usrP);
}
PETSC_EXTERN void  taogetapplicationcontext_(Tao tao,void*usrP, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoGetApplicationContext(
	(Tao)PetscToPointer((tao) ),usrP);
}
PETSC_EXTERN void  taosetgradientnorm_(Tao tao,Mat M, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(M);
*ierr = TaoSetGradientNorm(
	(Tao)PetscToPointer((tao) ),
	(Mat)PetscToPointer((M) ));
}
PETSC_EXTERN void  taogetgradientnorm_(Tao tao,Mat *M, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool M_null = !*(void**) M ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(M);
*ierr = TaoGetGradientNorm(
	(Tao)PetscToPointer((tao) ),M);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! M_null && !*(void**) M) * (void **) M = (void *)-2;
}
PETSC_EXTERN void  taogradientnorm_(Tao tao,Vec gradient,NormType *type,PetscReal *gnorm, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(gradient);
CHKFORTRANNULLREAL(gnorm);
*ierr = TaoGradientNorm(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((gradient) ),*type,gnorm);
}
#if defined(__cplusplus)
}
#endif
