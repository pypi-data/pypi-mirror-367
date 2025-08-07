#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plextrcohesive.c */
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

#include "petscdmplextransform.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformcohesiveextrudegettensor_ DMPLEXTRANSFORMCOHESIVEEXTRUDEGETTENSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformcohesiveextrudegettensor_ dmplextransformcohesiveextrudegettensor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformcohesiveextrudesettensor_ DMPLEXTRANSFORMCOHESIVEEXTRUDESETTENSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformcohesiveextrudesettensor_ dmplextransformcohesiveextrudesettensor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformcohesiveextrudegetwidth_ DMPLEXTRANSFORMCOHESIVEEXTRUDEGETWIDTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformcohesiveextrudegetwidth_ dmplextransformcohesiveextrudegetwidth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformcohesiveextrudesetwidth_ DMPLEXTRANSFORMCOHESIVEEXTRUDESETWIDTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformcohesiveextrudesetwidth_ dmplextransformcohesiveextrudesetwidth
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplextransformcohesiveextrudegettensor_(DMPlexTransform tr,PetscBool *useTensor, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformCohesiveExtrudeGetTensor(
	(DMPlexTransform)PetscToPointer((tr) ),useTensor);
}
PETSC_EXTERN void  dmplextransformcohesiveextrudesettensor_(DMPlexTransform tr,PetscBool *useTensor, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformCohesiveExtrudeSetTensor(
	(DMPlexTransform)PetscToPointer((tr) ),*useTensor);
}
PETSC_EXTERN void  dmplextransformcohesiveextrudegetwidth_(DMPlexTransform tr,PetscReal *width, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLREAL(width);
*ierr = DMPlexTransformCohesiveExtrudeGetWidth(
	(DMPlexTransform)PetscToPointer((tr) ),width);
}
PETSC_EXTERN void  dmplextransformcohesiveextrudesetwidth_(DMPlexTransform tr,PetscReal *width, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformCohesiveExtrudeSetWidth(
	(DMPlexTransform)PetscToPointer((tr) ),*width);
}
#if defined(__cplusplus)
}
#endif
