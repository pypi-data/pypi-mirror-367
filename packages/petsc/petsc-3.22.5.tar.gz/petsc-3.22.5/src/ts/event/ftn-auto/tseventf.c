#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* tsevent.c */
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
#define tssetposteventstep_ TSSETPOSTEVENTSTEP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssetposteventstep_ tssetposteventstep
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssetposteventsecondstep_ TSSETPOSTEVENTSECONDSTEP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssetposteventsecondstep_ tssetposteventsecondstep
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsseteventtolerances_ TSSETEVENTTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsseteventtolerances_ tsseteventtolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsgetnumevents_ TSGETNUMEVENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsgetnumevents_ tsgetnumevents
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tssetposteventstep_(TS ts,PetscReal *dt1, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSetPostEventStep(
	(TS)PetscToPointer((ts) ),*dt1);
}
PETSC_EXTERN void  tssetposteventsecondstep_(TS ts,PetscReal *dt2, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSetPostEventSecondStep(
	(TS)PetscToPointer((ts) ),*dt2);
}
PETSC_EXTERN void  tsseteventtolerances_(TS ts,PetscReal *tol,PetscReal vtol[], int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLREAL(vtol);
*ierr = TSSetEventTolerances(
	(TS)PetscToPointer((ts) ),*tol,vtol);
}
PETSC_EXTERN void  tsgetnumevents_(TS ts,PetscInt *nevents, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(nevents);
*ierr = TSGetNumEvents(
	(TS)PetscToPointer((ts) ),nevents);
}
#if defined(__cplusplus)
}
#endif
