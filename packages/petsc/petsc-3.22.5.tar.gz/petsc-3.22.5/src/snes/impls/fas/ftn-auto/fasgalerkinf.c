#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fasgalerkin.c */
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
#define snesfasgetgalerkin_ SNESFASGETGALERKIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetgalerkin_ snesfasgetgalerkin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetgalerkin_ SNESFASSETGALERKIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetgalerkin_ snesfassetgalerkin
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snesfasgetgalerkin_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASGetGalerkin(
	(SNES)PetscToPointer((snes) ),flg);
}
PETSC_EXTERN void  snesfassetgalerkin_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASSetGalerkin(
	(SNES)PetscToPointer((snes) ),*flg);
}
#if defined(__cplusplus)
}
#endif
