#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fretrieve.c */
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

#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsharedtmp_ PETSCSHAREDTMP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsharedtmp_ petscsharedtmp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsharedworkingdirectory_ PETSCSHAREDWORKINGDIRECTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsharedworkingdirectory_ petscsharedworkingdirectory
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsharedtmp_(MPI_Fint * comm,PetscBool *shared, int *ierr)
{
*ierr = PetscSharedTmp(
	MPI_Comm_f2c(*(comm)),shared);
}
PETSC_EXTERN void  petscsharedworkingdirectory_(MPI_Fint * comm,PetscBool *shared, int *ierr)
{
*ierr = PetscSharedWorkingDirectory(
	MPI_Comm_f2c(*(comm)),shared);
}
#if defined(__cplusplus)
}
#endif
