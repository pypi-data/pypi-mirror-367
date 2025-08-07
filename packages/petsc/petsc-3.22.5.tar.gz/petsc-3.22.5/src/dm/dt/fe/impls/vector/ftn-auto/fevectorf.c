#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fevector.c */
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
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfecreatevector_ PETSCFECREATEVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfecreatevector_ petscfecreatevector
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscfecreatevector_(PetscFE scalar_fe,PetscInt *num_copies,PetscBool *interleave_basis,PetscBool *interleave_components,PetscFE *vector_fe, int *ierr)
{
CHKFORTRANNULLOBJECT(scalar_fe);
PetscBool vector_fe_null = !*(void**) vector_fe ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vector_fe);
*ierr = PetscFECreateVector(
	(PetscFE)PetscToPointer((scalar_fe) ),*num_copies,*interleave_basis,*interleave_components,vector_fe);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vector_fe_null && !*(void**) vector_fe) * (void **) vector_fe = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
