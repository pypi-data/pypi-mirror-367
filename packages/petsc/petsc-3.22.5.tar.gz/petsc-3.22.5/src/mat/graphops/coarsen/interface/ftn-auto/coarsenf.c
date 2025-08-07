#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* coarsen.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsengettype_ MATCOARSENGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsengettype_ matcoarsengettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsenapply_ MATCOARSENAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsenapply_ matcoarsenapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsensetadjacency_ MATCOARSENSETADJACENCY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsensetadjacency_ matcoarsensetadjacency
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsensetstrictaggs_ MATCOARSENSETSTRICTAGGS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsensetstrictaggs_ matcoarsensetstrictaggs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsendestroy_ MATCOARSENDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsendestroy_ matcoarsendestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsenviewfromoptions_ MATCOARSENVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsenviewfromoptions_ matcoarsenviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsenview_ MATCOARSENVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsenview_ matcoarsenview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsensettype_ MATCOARSENSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsensettype_ matcoarsensettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsensetgreedyordering_ MATCOARSENSETGREEDYORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsensetgreedyordering_ matcoarsensetgreedyordering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsensetfromoptions_ MATCOARSENSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsensetfromoptions_ matcoarsensetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsensetmaximumiterations_ MATCOARSENSETMAXIMUMITERATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsensetmaximumiterations_ matcoarsensetmaximumiterations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsensetstrengthindex_ MATCOARSENSETSTRENGTHINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsensetstrengthindex_ matcoarsensetstrengthindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsensetthreshold_ MATCOARSENSETTHRESHOLD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsensetthreshold_ matcoarsensetthreshold
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoarsencreate_ MATCOARSENCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoarsencreate_ matcoarsencreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcoarsengettype_(MatCoarsen coarsen,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(coarsen);
*ierr = MatCoarsenGetType(
	(MatCoarsen)PetscToPointer((coarsen) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  matcoarsenapply_(MatCoarsen coarser, int *ierr)
{
CHKFORTRANNULLOBJECT(coarser);
*ierr = MatCoarsenApply(
	(MatCoarsen)PetscToPointer((coarser) ));
}
PETSC_EXTERN void  matcoarsensetadjacency_(MatCoarsen agg,Mat adj, int *ierr)
{
CHKFORTRANNULLOBJECT(agg);
CHKFORTRANNULLOBJECT(adj);
*ierr = MatCoarsenSetAdjacency(
	(MatCoarsen)PetscToPointer((agg) ),
	(Mat)PetscToPointer((adj) ));
}
PETSC_EXTERN void  matcoarsensetstrictaggs_(MatCoarsen agg,PetscBool *str, int *ierr)
{
CHKFORTRANNULLOBJECT(agg);
*ierr = MatCoarsenSetStrictAggs(
	(MatCoarsen)PetscToPointer((agg) ),*str);
}
PETSC_EXTERN void  matcoarsendestroy_(MatCoarsen *agg, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(agg);
 PetscBool agg_null = !*(void**) agg ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(agg);
*ierr = MatCoarsenDestroy(agg);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! agg_null && !*(void**) agg) * (void **) agg = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(agg);
 }
PETSC_EXTERN void  matcoarsenviewfromoptions_(MatCoarsen A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = MatCoarsenViewFromOptions(
	(MatCoarsen)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  matcoarsenview_(MatCoarsen agg,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(agg);
CHKFORTRANNULLOBJECT(viewer);
*ierr = MatCoarsenView(
	(MatCoarsen)PetscToPointer((agg) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  matcoarsensettype_(MatCoarsen coarser,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(coarser);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = MatCoarsenSetType(
	(MatCoarsen)PetscToPointer((coarser) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  matcoarsensetgreedyordering_(MatCoarsen coarser, IS perm, int *ierr)
{
CHKFORTRANNULLOBJECT(coarser);
CHKFORTRANNULLOBJECT(perm);
*ierr = MatCoarsenSetGreedyOrdering(
	(MatCoarsen)PetscToPointer((coarser) ),
	(IS)PetscToPointer((perm) ));
}
PETSC_EXTERN void  matcoarsensetfromoptions_(MatCoarsen coarser, int *ierr)
{
CHKFORTRANNULLOBJECT(coarser);
*ierr = MatCoarsenSetFromOptions(
	(MatCoarsen)PetscToPointer((coarser) ));
}
PETSC_EXTERN void  matcoarsensetmaximumiterations_(MatCoarsen coarse,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(coarse);
*ierr = MatCoarsenSetMaximumIterations(
	(MatCoarsen)PetscToPointer((coarse) ),*n);
}
PETSC_EXTERN void  matcoarsensetstrengthindex_(MatCoarsen coarse,PetscInt *n,PetscInt idx[], int *ierr)
{
CHKFORTRANNULLOBJECT(coarse);
CHKFORTRANNULLINTEGER(idx);
*ierr = MatCoarsenSetStrengthIndex(
	(MatCoarsen)PetscToPointer((coarse) ),*n,idx);
}
PETSC_EXTERN void  matcoarsensetthreshold_(MatCoarsen coarse,PetscReal *b, int *ierr)
{
CHKFORTRANNULLOBJECT(coarse);
*ierr = MatCoarsenSetThreshold(
	(MatCoarsen)PetscToPointer((coarse) ),*b);
}
PETSC_EXTERN void  matcoarsencreate_(MPI_Fint * comm,MatCoarsen *newcrs, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(newcrs);
 PetscBool newcrs_null = !*(void**) newcrs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newcrs);
*ierr = MatCoarsenCreate(
	MPI_Comm_f2c(*(comm)),newcrs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newcrs_null && !*(void**) newcrs) * (void **) newcrs = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
