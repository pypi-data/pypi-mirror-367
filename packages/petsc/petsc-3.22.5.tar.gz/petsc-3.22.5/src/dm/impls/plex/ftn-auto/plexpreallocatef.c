#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexpreallocate.c */
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

#include "petscdmplex.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexpreallocateoperator_ DMPLEXPREALLOCATEOPERATOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexpreallocateoperator_ dmplexpreallocateoperator
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexpreallocateoperator_(DM dm,PetscInt *bs,PetscInt dnz[],PetscInt onz[],PetscInt dnzu[],PetscInt onzu[],Mat A,PetscBool *fillMatrix, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(dnz);
CHKFORTRANNULLINTEGER(onz);
CHKFORTRANNULLINTEGER(dnzu);
CHKFORTRANNULLINTEGER(onzu);
CHKFORTRANNULLOBJECT(A);
*ierr = DMPlexPreallocateOperator(
	(DM)PetscToPointer((dm) ),*bs,dnz,onz,dnzu,onzu,
	(Mat)PetscToPointer((A) ),*fillMatrix);
}
#if defined(__cplusplus)
}
#endif
