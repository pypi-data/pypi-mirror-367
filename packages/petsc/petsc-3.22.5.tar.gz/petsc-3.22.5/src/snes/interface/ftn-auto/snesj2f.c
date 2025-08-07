#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* snesj2.c */
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

#include "petscsnes.h"
#include "petscdm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescomputejacobiandefaultcolor_ SNESCOMPUTEJACOBIANDEFAULTCOLOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescomputejacobiandefaultcolor_ snescomputejacobiandefaultcolor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesprunejacobiancolor_ SNESPRUNEJACOBIANCOLOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesprunejacobiancolor_ snesprunejacobiancolor
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snescomputejacobiandefaultcolor_(SNES snes,Vec x1,Mat J,Mat B,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(x1);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(B);
*ierr = SNESComputeJacobianDefaultColor(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((x1) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((B) ),ctx);
}
PETSC_EXTERN void  snesprunejacobiancolor_(SNES snes,Mat J,Mat B, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(B);
*ierr = SNESPruneJacobianColor(
	(SNES)PetscToPointer((snes) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((B) ));
}
#if defined(__cplusplus)
}
#endif
