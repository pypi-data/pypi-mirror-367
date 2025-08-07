#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pinit.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinitialized_ PETSCINITIALIZED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinitialized_ petscinitialized
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfinalized_ PETSCFINALIZED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfinalized_ petscfinalized
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmaxsum_ PETSCMAXSUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmaxsum_ petscmaxsum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfinalize_ PETSCFINALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfinalize_ petscfinalize
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscinitialized_(PetscBool *isInitialized, int *ierr)
{
*ierr = PetscInitialized(isInitialized);
}
PETSC_EXTERN void  petscfinalized_(PetscBool *isFinalized, int *ierr)
{
*ierr = PetscFinalized(isFinalized);
}
PETSC_EXTERN void  petscmaxsum_(MPI_Fint * comm, PetscInt array[],PetscInt *max,PetscInt *sum, int *ierr)
{
CHKFORTRANNULLINTEGER(array);
CHKFORTRANNULLINTEGER(max);
CHKFORTRANNULLINTEGER(sum);
*ierr = PetscMaxSum(
	MPI_Comm_f2c(*(comm)),array,max,sum);
}
PETSC_EXTERN void  petscfinalize_(int *ierr)
{
*ierr = PetscFinalize();
}
#if defined(__cplusplus)
}
#endif
