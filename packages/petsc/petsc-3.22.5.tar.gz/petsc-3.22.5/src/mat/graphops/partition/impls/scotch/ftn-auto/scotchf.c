#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* scotch.c */
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
#define matpartitioningptscotchsetimbalance_ MATPARTITIONINGPTSCOTCHSETIMBALANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningptscotchsetimbalance_ matpartitioningptscotchsetimbalance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningptscotchgetimbalance_ MATPARTITIONINGPTSCOTCHGETIMBALANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningptscotchgetimbalance_ matpartitioningptscotchgetimbalance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningptscotchsetstrategy_ MATPARTITIONINGPTSCOTCHSETSTRATEGY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningptscotchsetstrategy_ matpartitioningptscotchsetstrategy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningptscotchgetstrategy_ MATPARTITIONINGPTSCOTCHGETSTRATEGY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningptscotchgetstrategy_ matpartitioningptscotchgetstrategy
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matpartitioningptscotchsetimbalance_(MatPartitioning part,PetscReal *imb, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningPTScotchSetImbalance(
	(MatPartitioning)PetscToPointer((part) ),*imb);
}
PETSC_EXTERN void  matpartitioningptscotchgetimbalance_(MatPartitioning part,PetscReal *imb, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
CHKFORTRANNULLREAL(imb);
*ierr = MatPartitioningPTScotchGetImbalance(
	(MatPartitioning)PetscToPointer((part) ),imb);
}
PETSC_EXTERN void  matpartitioningptscotchsetstrategy_(MatPartitioning part,MPPTScotchStrategyType *strategy, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningPTScotchSetStrategy(
	(MatPartitioning)PetscToPointer((part) ),*strategy);
}
PETSC_EXTERN void  matpartitioningptscotchgetstrategy_(MatPartitioning part,MPPTScotchStrategyType *strategy, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningPTScotchGetStrategy(
	(MatPartitioning)PetscToPointer((part) ),strategy);
}
#if defined(__cplusplus)
}
#endif
