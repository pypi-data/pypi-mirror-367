#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pcmat.c */
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

#include "petscpc.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmatsetapplyoperation_ PCMATSETAPPLYOPERATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmatsetapplyoperation_ pcmatsetapplyoperation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmatgetapplyoperation_ PCMATGETAPPLYOPERATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmatgetapplyoperation_ pcmatgetapplyoperation
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcmatsetapplyoperation_(PC pc,MatOperation *matop, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMatSetApplyOperation(
	(PC)PetscToPointer((pc) ),*matop);
}
PETSC_EXTERN void  pcmatgetapplyoperation_(PC pc,MatOperation *matop, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMatGetApplyOperation(
	(PC)PetscToPointer((pc) ),matop);
}
#if defined(__cplusplus)
}
#endif
