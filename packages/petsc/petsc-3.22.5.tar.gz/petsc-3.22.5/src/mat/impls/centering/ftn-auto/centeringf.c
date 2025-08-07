#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* centering.c */
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
#define matcreatecentering_ MATCREATECENTERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatecentering_ matcreatecentering
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreatecentering_(MPI_Fint * comm,PetscInt *n,PetscInt *N,Mat *C, int *ierr)
{
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatCreateCentering(
	MPI_Comm_f2c(*(comm)),*n,*N,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
