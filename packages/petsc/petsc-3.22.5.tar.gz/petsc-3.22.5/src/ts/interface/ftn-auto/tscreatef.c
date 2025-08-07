#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* tscreate.c */
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
#define tscreate_ TSCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tscreate_ tscreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tscreate_(MPI_Fint * comm,TS *ts, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(ts);
 PetscBool ts_null = !*(void**) ts ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ts);
*ierr = TSCreate(
	MPI_Comm_f2c(*(comm)),ts);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ts_null && !*(void**) ts) * (void **) ts = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
