#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* ssp.c */
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
#define tssspsettype_ TSSSPSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssspsettype_ tssspsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssspgettype_ TSSSPGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssspgettype_ tssspgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssspsetnumstages_ TSSSPSETNUMSTAGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssspsetnumstages_ tssspsetnumstages
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssspgetnumstages_ TSSSPGETNUMSTAGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssspgetnumstages_ tssspgetnumstages
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tssspsettype_(TS ts,char *ssptype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for ssptype */
  FIXCHAR(ssptype,cl0,_cltmp0);
*ierr = TSSSPSetType(
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(ssptype,_cltmp0);
}
PETSC_EXTERN void  tssspgettype_(TS ts,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSSPGetType(
	(TS)PetscToPointer((ts) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  tssspsetnumstages_(TS ts,PetscInt *nstages, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSSPSetNumStages(
	(TS)PetscToPointer((ts) ),*nstages);
}
PETSC_EXTERN void  tssspgetnumstages_(TS ts,PetscInt *nstages, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(nstages);
*ierr = TSSSPGetNumStages(
	(TS)PetscToPointer((ts) ),nstages);
}
#if defined(__cplusplus)
}
#endif
