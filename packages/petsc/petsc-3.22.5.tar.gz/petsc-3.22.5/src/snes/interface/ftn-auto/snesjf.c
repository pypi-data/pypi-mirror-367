#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* snesj.c */
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
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescomputejacobiandefault_ SNESCOMPUTEJACOBIANDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescomputejacobiandefault_ snescomputejacobiandefault
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snescomputejacobiandefault_(SNES snes,Vec x1,Mat J,Mat B,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(x1);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(B);
*ierr = SNESComputeJacobianDefault(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((x1) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((B) ),ctx);
}
#if defined(__cplusplus)
}
#endif
