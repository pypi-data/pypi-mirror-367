#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plextrextrude.c */
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
#define dmplextransformextrudegetlayers_ DMPLEXTRANSFORMEXTRUDEGETLAYERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudegetlayers_ dmplextransformextrudegetlayers
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudesetlayers_ DMPLEXTRANSFORMEXTRUDESETLAYERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudesetlayers_ dmplextransformextrudesetlayers
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudegetthickness_ DMPLEXTRANSFORMEXTRUDEGETTHICKNESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudegetthickness_ dmplextransformextrudegetthickness
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudesetthickness_ DMPLEXTRANSFORMEXTRUDESETTHICKNESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudesetthickness_ dmplextransformextrudesetthickness
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudegettensor_ DMPLEXTRANSFORMEXTRUDEGETTENSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudegettensor_ dmplextransformextrudegettensor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudesettensor_ DMPLEXTRANSFORMEXTRUDESETTENSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudesettensor_ dmplextransformextrudesettensor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudegetsymmetric_ DMPLEXTRANSFORMEXTRUDEGETSYMMETRIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudegetsymmetric_ dmplextransformextrudegetsymmetric
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudesetsymmetric_ DMPLEXTRANSFORMEXTRUDESETSYMMETRIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudesetsymmetric_ dmplextransformextrudesetsymmetric
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudegetperiodic_ DMPLEXTRANSFORMEXTRUDEGETPERIODIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudegetperiodic_ dmplextransformextrudegetperiodic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudesetperiodic_ DMPLEXTRANSFORMEXTRUDESETPERIODIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudesetperiodic_ dmplextransformextrudesetperiodic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudegetnormal_ DMPLEXTRANSFORMEXTRUDEGETNORMAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudegetnormal_ dmplextransformextrudegetnormal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudesetnormal_ DMPLEXTRANSFORMEXTRUDESETNORMAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudesetnormal_ dmplextransformextrudesetnormal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformextrudesetthicknesses_ DMPLEXTRANSFORMEXTRUDESETTHICKNESSES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformextrudesetthicknesses_ dmplextransformextrudesetthicknesses
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplextransformextrudegetlayers_(DMPlexTransform tr,PetscInt *layers, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLINTEGER(layers);
*ierr = DMPlexTransformExtrudeGetLayers(
	(DMPlexTransform)PetscToPointer((tr) ),layers);
}
PETSC_EXTERN void  dmplextransformextrudesetlayers_(DMPlexTransform tr,PetscInt *layers, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformExtrudeSetLayers(
	(DMPlexTransform)PetscToPointer((tr) ),*layers);
}
PETSC_EXTERN void  dmplextransformextrudegetthickness_(DMPlexTransform tr,PetscReal *thickness, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLREAL(thickness);
*ierr = DMPlexTransformExtrudeGetThickness(
	(DMPlexTransform)PetscToPointer((tr) ),thickness);
}
PETSC_EXTERN void  dmplextransformextrudesetthickness_(DMPlexTransform tr,PetscReal *thickness, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformExtrudeSetThickness(
	(DMPlexTransform)PetscToPointer((tr) ),*thickness);
}
PETSC_EXTERN void  dmplextransformextrudegettensor_(DMPlexTransform tr,PetscBool *useTensor, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformExtrudeGetTensor(
	(DMPlexTransform)PetscToPointer((tr) ),useTensor);
}
PETSC_EXTERN void  dmplextransformextrudesettensor_(DMPlexTransform tr,PetscBool *useTensor, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformExtrudeSetTensor(
	(DMPlexTransform)PetscToPointer((tr) ),*useTensor);
}
PETSC_EXTERN void  dmplextransformextrudegetsymmetric_(DMPlexTransform tr,PetscBool *symmetric, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformExtrudeGetSymmetric(
	(DMPlexTransform)PetscToPointer((tr) ),symmetric);
}
PETSC_EXTERN void  dmplextransformextrudesetsymmetric_(DMPlexTransform tr,PetscBool *symmetric, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformExtrudeSetSymmetric(
	(DMPlexTransform)PetscToPointer((tr) ),*symmetric);
}
PETSC_EXTERN void  dmplextransformextrudegetperiodic_(DMPlexTransform tr,PetscBool *periodic, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformExtrudeGetPeriodic(
	(DMPlexTransform)PetscToPointer((tr) ),periodic);
}
PETSC_EXTERN void  dmplextransformextrudesetperiodic_(DMPlexTransform tr,PetscBool *periodic, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformExtrudeSetPeriodic(
	(DMPlexTransform)PetscToPointer((tr) ),*periodic);
}
PETSC_EXTERN void  dmplextransformextrudegetnormal_(DMPlexTransform tr,PetscReal normal[], int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLREAL(normal);
*ierr = DMPlexTransformExtrudeGetNormal(
	(DMPlexTransform)PetscToPointer((tr) ),normal);
}
PETSC_EXTERN void  dmplextransformextrudesetnormal_(DMPlexTransform tr, PetscReal normal[], int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLREAL(normal);
*ierr = DMPlexTransformExtrudeSetNormal(
	(DMPlexTransform)PetscToPointer((tr) ),normal);
}
PETSC_EXTERN void  dmplextransformextrudesetthicknesses_(DMPlexTransform tr,PetscInt *Nth, PetscReal thicknesses[], int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLREAL(thicknesses);
*ierr = DMPlexTransformExtrudeSetThicknesses(
	(DMPlexTransform)PetscToPointer((tr) ),*Nth,thicknesses);
}
#if defined(__cplusplus)
}
#endif
