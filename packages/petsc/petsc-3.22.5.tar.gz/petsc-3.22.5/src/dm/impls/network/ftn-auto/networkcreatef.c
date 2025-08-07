#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* networkcreate.c */
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

#include "petscdmnetwork.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkcreate_ DMNETWORKCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkcreate_ dmnetworkcreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmnetworkcreate_(MPI_Fint * comm,DM *network, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(network);
 PetscBool network_null = !*(void**) network ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(network);
*ierr = DMNetworkCreate(
	MPI_Comm_f2c(*(comm)),network);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! network_null && !*(void**) network) * (void **) network = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
