#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* spacepoint.c */
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

#include "petscfe.h"
#include "petscdt.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacepointsetpoints_ PETSCSPACEPOINTSETPOINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacepointsetpoints_ petscspacepointsetpoints
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacepointgetpoints_ PETSCSPACEPOINTGETPOINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacepointgetpoints_ petscspacepointgetpoints
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscspacepointsetpoints_(PetscSpace sp,PetscQuadrature q, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLOBJECT(q);
*ierr = PetscSpacePointSetPoints(
	(PetscSpace)PetscToPointer((sp) ),
	(PetscQuadrature)PetscToPointer((q) ));
}
PETSC_EXTERN void  petscspacepointgetpoints_(PetscSpace sp,PetscQuadrature *q, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool q_null = !*(void**) q ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(q);
*ierr = PetscSpacePointGetPoints(
	(PetscSpace)PetscToPointer((sp) ),q);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! q_null && !*(void**) q) * (void **) q = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
