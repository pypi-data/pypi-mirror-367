#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmredundant.c */
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

#include "petscdmredundant.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmredundantsetsize_ DMREDUNDANTSETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmredundantsetsize_ dmredundantsetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmredundantgetsize_ DMREDUNDANTGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmredundantgetsize_ dmredundantgetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmredundantcreate_ DMREDUNDANTCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmredundantcreate_ dmredundantcreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmredundantsetsize_(DM dm,PetscMPIInt *rank,PetscInt *N, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMRedundantSetSize(
	(DM)PetscToPointer((dm) ),*rank,*N);
}
PETSC_EXTERN void  dmredundantgetsize_(DM dm,PetscMPIInt *rank,PetscInt *N, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(N);
*ierr = DMRedundantGetSize(
	(DM)PetscToPointer((dm) ),rank,N);
}
PETSC_EXTERN void  dmredundantcreate_(MPI_Fint * comm,PetscMPIInt *rank,PetscInt *N,DM *dm, int *ierr)
{
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMRedundantCreate(
	MPI_Comm_f2c(*(comm)),*rank,*N,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
