#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* irk.c */
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

#include "petscts.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsirksettype_ TSIRKSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsirksettype_ tsirksettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsirkgettype_ TSIRKGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsirkgettype_ tsirkgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsirksetnumstages_ TSIRKSETNUMSTAGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsirksetnumstages_ tsirksetnumstages
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsirkgetnumstages_ TSIRKGETNUMSTAGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsirkgetnumstages_ tsirkgetnumstages
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsirksettype_(TS ts,char *irktype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for irktype */
  FIXCHAR(irktype,cl0,_cltmp0);
*ierr = TSIRKSetType(
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(irktype,_cltmp0);
}
PETSC_EXTERN void  tsirkgettype_(TS ts,char *irktype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
*ierr = TSIRKGetType(
	(TS)PetscToPointer((ts) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for irktype */
*ierr = PetscStrncpy(irktype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, irktype, cl0);
}
PETSC_EXTERN void  tsirksetnumstages_(TS ts,PetscInt *nstages, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSIRKSetNumStages(
	(TS)PetscToPointer((ts) ),*nstages);
}
PETSC_EXTERN void  tsirkgetnumstages_(TS ts,PetscInt *nstages, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(nstages);
*ierr = TSIRKGetNumStages(
	(TS)PetscToPointer((ts) ),nstages);
}
#if defined(__cplusplus)
}
#endif
