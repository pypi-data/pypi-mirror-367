#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* stride.c */
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

#include "petscis.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isstridegetinfo_ ISSTRIDEGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isstridegetinfo_ isstridegetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isstridesetstride_ ISSTRIDESETSTRIDE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isstridesetstride_ isstridesetstride
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscreatestride_ ISCREATESTRIDE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscreatestride_ iscreatestride
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  isstridegetinfo_(IS is,PetscInt *first,PetscInt *step, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(first);
CHKFORTRANNULLINTEGER(step);
*ierr = ISStrideGetInfo(
	(IS)PetscToPointer((is) ),first,step);
}
PETSC_EXTERN void  isstridesetstride_(IS is,PetscInt *n,PetscInt *first,PetscInt *step, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISStrideSetStride(
	(IS)PetscToPointer((is) ),*n,*first,*step);
}
PETSC_EXTERN void  iscreatestride_(MPI_Fint * comm,PetscInt *n,PetscInt *first,PetscInt *step,IS *is, int *ierr)
{
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = ISCreateStride(
	MPI_Comm_f2c(*(comm)),*n,*first,*step,is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
