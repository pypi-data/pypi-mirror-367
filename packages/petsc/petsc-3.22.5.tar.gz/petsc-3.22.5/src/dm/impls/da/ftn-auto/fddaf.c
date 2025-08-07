#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fdda.c */
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

#include "petscdmda.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdasetblockfills_ DMDASETBLOCKFILLS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdasetblockfills_ dmdasetblockfills
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdasetblockfillssparse_ DMDASETBLOCKFILLSSPARSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdasetblockfillssparse_ dmdasetblockfillssparse
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmdasetblockfills_(DM da, PetscInt *dfill, PetscInt *ofill, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
CHKFORTRANNULLINTEGER(dfill);
CHKFORTRANNULLINTEGER(ofill);
*ierr = DMDASetBlockFills(
	(DM)PetscToPointer((da) ),dfill,ofill);
}
PETSC_EXTERN void  dmdasetblockfillssparse_(DM da, PetscInt *dfillsparse, PetscInt *ofillsparse, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
CHKFORTRANNULLINTEGER(dfillsparse);
CHKFORTRANNULLINTEGER(ofillsparse);
*ierr = DMDASetBlockFillsSparse(
	(DM)PetscToPointer((da) ),dfillsparse,ofillsparse);
}
#if defined(__cplusplus)
}
#endif
